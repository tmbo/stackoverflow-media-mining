import mysql.connector
from mysql.connector import errorcode
import re
from gensim import utils, models, corpora
from text_features import removeTags, removeCode
from tagging import TextChunker
import multiprocessing
import os
from operator import itemgetter
import logging
import nltk
from curses.ascii import isdigit
from syllablecounter import cmusyllables

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

chunker = TextChunker(stemChunks=False)

syl_counter = cmusyllables()

class SOQuestionCorpus(object):
    def __init__(self, questions, isAlreadyTokenized):
        self.questions = questions
        self.isAlreadyTokenized = isAlreadyTokenized
        print "Creating dictionary..."
        self.dictionary = corpora.Dictionary(self.tokenized_texts())
        self.dictionary.filter_extremes(no_above=0.9)  # remove stopwords etc

    def __iter__(self):
        for tokens in self.tokenized_texts():
            yield self.dictionary.doc2bow(tokens)

    def tokenized_texts(self):
        return self.questions if self.isAlreadyTokenized else self.iter_texts(self.questions)

    def iter_texts(self, tag_free_texts):
        return map(lambda text: utils.simple_preprocess(text), tag_free_texts)


class TopicModel:
    def __init__(self, name, model, dictionary, preprocessor):
        self.model = model
        self.dictionary = dictionary
        self.name = name
        self.preprocessor = preprocessor

    @staticmethod
    def create(name, questions, isAlreadyTokenized, preprocessor):
        corpus = SOQuestionCorpus(questions, isAlreadyTokenized)
        mallet_path = 'mallet/bin/mallet'
        model = models.LdaMallet(mallet_path, corpus, num_topics=100, iterations=1000, workers=6, id2word=corpus.dictionary)
        return TopicModel(name, model, corpus.dictionary, preprocessor)

    @staticmethod
    def load_from_file(name, preprocessor):
        return TopicModel(name, models.LdaMallet.load("output/%s_model.lda" % name), corpora.Dictionary.load("output/%s_dictionary.lda" % name), preprocessor)

    def topics(self, text):
        return self.model[self.text_to_bow(text)]

    def text_to_bow(self, text):
        return self.dictionary.doc2bow(self.preprocessor(text))

    def save(self):
        self.model.save("output/%s_model.lda" % self.name)
        self.dictionary.save("output/%s_dictionary.lda" % self.name)


def preprocessQuestion(question):
    return list(chunker.chunkText(question.lower()))


def create_topic_models(questions):
    whole = TopicModel("whole_question", questions, isAlreadyTokenized=False)

    print "Chunking text..."
    chunked = pool.map(preprocessQuestion, questions)
    pool.terminate()
    print "Finished chunking text..."
    vp = TopicModel("VP_question", chunked, isAlreadyTokenized=True)
    return whole, vp


def extract_best_topics(els, n):
    sorted_by_second = sorted(els, key=itemgetter(1), reverse=True)
    return map(itemgetter(0), sorted_by_second[0:n])


def updateTopicFeatures(data, cursor, writer):
    try:
        query = """UPDATE training_features SET topic1=%s,topic2=%s,topic3=%s,vp_topic1=%s,vp_topic2=%s,vp_topic3=%s, body_ari=%s, body_cli=%s, body_fki=%s WHERE QuestionId=%s"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN UPDATE: "
        print err
        raise


def count_characters(text):
    count = 0
    punctuation = ['.', ',', '!', '?', ';', ':']
    for c in text:
        if c.isalnum or c in punctuation:
            count += 1
    return count


def automated_readability_index(stats):
    return 4.71 * (stats['chars'] / stats['words']) + 0.5 * (stats['words'] / stats['sentences']) - 21.43


def coleman_liau_index(stats):
    return 0.0588 * (stats['chars'] * 100 / stats['words']) - 0.296 * (stats['sentences'] * 100 / stats['words']) - 15.8


def flesch_kincaid_index(stats):
    return 0.39 * (stats['words'] / stats['sentences']) + 11.8 * (stats['syllables'] / stats['words']) - 15.59


def count_syllables(sentences):
    syl_count = 0
    for sentence in sentences:
        for word in sentence:
            syl_count += syl_counter.SyllableCount(word)
    return syl_count


def calculate_stats(text):
    sentences = nltk.sent_tokenize(text)
    words = [nltk.word_tokenize(sent) for sent in sentences]

    return {
        'words': sum(map(lambda s: len(s), words)),
        'sentences': len(sentences),
        'chars': count_characters(text),
        'syllables': count_syllables(words)
    }


# pool = multiprocessing.Pool()

if __name__ == "__main__":

    try:
        wholeName = "whole_question"
        vpName = "VP_question"

        FlushSize = 500

        cnx = mysql.connector.connect(user="root",
                                      database="stackoverflow",
                                      host="localhost")

        print "Starting number crunching\n"

        cursor = cnx.cursor()
        cursor.execute("Select PostId, Body FROM bounty_text LIMIT 100")

        # HACKY
        print "Fetching questions..."
        rows = cursor.fetchall()

        questions = map(lambda row: removeTags(removeCode(row[1].encode("utf-8"))), rows)

        if os.path.isfile("output/%s_model.lda" % wholeName):
            whole_model = TopicModel.load_from_file(wholeName, utils.simple_preprocess)
        else:
            whole_model = TopicModel.create(wholeName, questions, False, utils.simple_preprocess)
            whole_model.save()

        print "Chunking text..."
        # if os.path.isfile("output/%s_model.lda" % vpName):
        #     vp_model = TopicModel.load_from_file(vpName, preprocessQuestion)
        # else:
        #     chunked = pool.map(preprocessQuestion, questions)
        #     pool.terminate()
        #     print "Finished chunking text..."
        #     vp_model = TopicModel.create(vpName, chunked, True, preprocessQuestion)
        #     vp_model.save()

        updateData = []

        for row in rows:
            body = removeTags(removeCode(row[1].encode("utf-8")))
            pred =  whole_model.topics(body)
            topics = extract_best_topics(pred, 3)
            # vp_topics = extract_best_topics(vp_model.topics(body), 3)
            data = topics
            # data.extend(vp_topics)
            stats = calculate_stats(body)
            data.append(automated_readability_index(stats))
            data.append(coleman_liau_index(stats))
            data.append(flesch_kincaid_index(stats))
            data.append(row[0])
            updateData.append(data)
            if len(updateData) > FlushSize:
                updateTopicFeatures(updateData, cursor, cnx)
                updateData = []

        if len(updateData) > 0:
            updateTopicFeatures(updateData, cursor, cnx)

        print "Done"

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exists")
        else:
            print(err)
    else:
        cnx.close()


