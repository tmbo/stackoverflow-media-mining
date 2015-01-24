import mysql.connector
from mysql.connector import errorcode
from gensim import utils, models, corpora
from text_features import removeTags, removeCode, number_of_code_snippets, lengthOfCodeSnippets, numberOfImages, textLength
from tagging import TextChunker
import multiprocessing
import os
from operator import itemgetter
import logging
from math import sqrt
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
        tokenized = self.tokenized_texts()
        self.dictionary = corpora.Dictionary(tokenized)
        self.dictionary.filter_extremes(no_above=0.5)  # remove stopwords etc
        self.underlying = [self.dictionary.doc2bow(tokens) for tokens in tokenized]

    def __len__(self):
        return len(self.questions)

    def __iter__(self):
        for bow in self.underlying:
            yield bow

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
        model = models.LdaModel(corpus, passes=20, num_topics=100, id2word=corpus.dictionary)
        return TopicModel(name, model, corpus.dictionary, preprocessor)

    @staticmethod
    def load_from_file(name, preprocessor):
        return TopicModel(name, models.LdaModel.load("output/%s_model.lda" % name), corpora.Dictionary.load("output/%s_dictionary.lda" % name), preprocessor)

    def topics(self, text, is_already_processed):
        return self.model[self.text_to_bow(text, is_already_processed)]

    def text_to_bow(self, text, is_already_processed):
        if not is_already_processed:
            text = self.preprocessor(text)
        return self.dictionary.doc2bow(text)

    def save(self):
        self.model.save("output/%s_model.lda" % self.name)
        self.dictionary.save("output/%s_dictionary.lda" % self.name)


def preprocessQuestion(question):
    return list(chunker.chunkText(question.lower()))


def extract_best_topics(els, n):
    sorted_by_second = sorted(els, key=itemgetter(1), reverse=True)
    return map(itemgetter(0), sorted_by_second[0:n])


def updateTopicFeatures(data, cursor, writer):
    try:
        query = """UPDATE training_features, bounties b
            SET body_avg_chars=%s, body_avg_words=%s, body_ari=%s, body_cli=%s, body_fre=%s, body_gfi=%s, topics=%s, vp_topics=%s
            WHERE b.QuestionId=%s and b.Id = training_features.Id"""
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
    try:
        return 4.71 * (stats['chars'] / stats['words']) + 0.5 * (stats['words'] / stats['sentences']) - 21.43
    except ZeroDivisionError:
        return 0


def coleman_liau_index(stats):
    try:
        return 0.0588 * (stats['chars'] * 100 / stats['words']) - 0.296 * (stats['sentences'] * 100 / stats['words']) - 15.8
    except ZeroDivisionError:
        return 0


def flesch_reading_ease(stats):
    try:
        return 206.835 - 1.015 * (stats['words'] / stats['sentences']) - 84.6 * (stats['syllables'] / stats['words'])
    except ZeroDivisionError:
        return 0


def gunning_fog_index(stats):
    try:
        return 0.4 * ((stats['words'] / stats['sentences'] + 100 * stats['polysyllables'] / stats['words']))

    except ZeroDivisionError:
        return 0


def count_syllables(words):
    return [syl_counter.SyllableCount(word) for word in words]


def calculate_stats(text):
    sentences = nltk.sent_tokenize(text)
    words = [token for sent in sentences for token in nltk.word_tokenize(sent) if len(token) >= 2 or token.lower() == "i"]
    syllables = count_syllables(words)

    avg_words = len(words) / len(sentences) if len(sentences) > 0 else 0
    avg_chars = count_characters(text) / len(words) if len(words) > 0 else 0

    return {
        'words': len(words),
        'avg_chars': avg_chars,
        'avg_words': avg_words,
        'sentences': len(sentences),
        'chars': count_characters(text),
        'syllables': sum(syllables),
        'polysyllables': len(filter(lambda num_word_syllables: num_word_syllables >= 3, syllables))
    }


def ensure_size(a, n, default):
    while len(a) < n:
        a.append(default)
    return a

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
        cursor.execute("Select PostId, Body FROM bounty_text")

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
        pool = multiprocessing.Pool()
        chunked = pool.map(preprocessQuestion, questions)
        pool.terminate()
        print "Finished chunking text..."

        if os.path.isfile("output/%s_model.lda" % vpName):
            vp_model = TopicModel.load_from_file(vpName, preprocessQuestion)
        else:
            vp_model = TopicModel.create(vpName, chunked, True, preprocessQuestion)
            vp_model.save()

        updateData = []

        for idx, row in enumerate(rows):
            body = removeTags(removeCode(row[1].encode("utf-8")))
            pred = whole_model.topics(body, False)
            topics = whole_model.topics(body, False)
            vp_topics = vp_model.topics(chunked[idx], True)

            data = []
            stats = calculate_stats(body)
            data.append(stats['avg_chars'])
            data.append(stats['avg_words'])
            data.append(automated_readability_index(stats))
            data.append(coleman_liau_index(stats))
            data.append(flesch_reading_ease(stats))
            data.append(gunning_fog_index(stats))
            data.append(str(topics))
            data.append(str(vp_topics))
            data.append(row[0])
            updateData.append(data)
            if len(updateData) > FlushSize:
                updateTopicFeatures(updateData, cursor, cnx)
                updateData = []
                print "Finished %d" % idx

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


