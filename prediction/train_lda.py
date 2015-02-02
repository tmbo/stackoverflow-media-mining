from gensim import utils, models, corpora
# from database import Database
#from text_features import removeTags, removeCode
from chunking import TextChunker
import os
import logging
import ConfigParser
import multiprocessing

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenizer = None


def _process_row(row):
    if row[1] is None:
        return row[0], []
    else:
        return row[0], list(tokenizer(removeTags(removeCode(row[1].encode("utf-8")))))


class SOQuestionCorpus(corpora.TextCorpus):
    def __init__(self, tokenizer, processes=None, query_page_size=50000, subsample=1.0):
        self.tokenizer = tokenizer
        self.processes = processes
        self.subsample = subsample
        self.query_page_size = query_page_size
        print "Creating dictionary..."
        super(SOQuestionCorpus, self).__init__(input=True)
        self.dictionary.filter_extremes(no_below=3, no_above=0.2)

    def get_texts(self):
        return self.question_body_stream()

    @staticmethod
    def pre_process(body):
        return removeTags(removeCode(body))

    def question_body_stream(self):
        global tokenizer
        tokenizer = self.tokenizer
        config = ConfigParser.RawConfigParser()
        config.read('application.cfg')
        db = Database(config)
        query_results = db.paged_query(select="Body", from_="posts", where="PostTypeId=1",
                                       page_size=self.query_page_size, subsample=self.subsample)
        pool = multiprocessing.Pool(self.processes)
        for page in query_results:
           for Id, tokens in pool.map(_process_row, page):
               if tokens:
                   yield tokens
               else:
                   print "ERROR in row %s" % Id
        pool.terminate()


class SOQuestionTopicModel(object):
    def __init__(self, name, model, dictionary, tokenizer):
        self.model = model
        self.dictionary = dictionary
        self.name = name
        self.tokenizer = tokenizer


    @staticmethod
    def train(name, tokenizer, num_topics=100, load_corpus_from_file=False, query_page_size=50000, subsample=1.0):
        if not load_corpus_from_file:
            corpus = SOQuestionCorpus(tokenizer, query_page_size=query_page_size, subsample=subsample)
            print "Storing corpus for %s name..." % name
            corpora.MmCorpus.serialize('output/%s.mm' % name, corpus, progress_cnt=10000)
            print "Storing dictionary for %s..." % name
            corpus.dictionary.save('output/%s.dict' % name)

        corpus = corpora.MmCorpus('output/%s.mm' % name)
        dictionary = corpora.Dictionary.load('output/%s.dict' % name)

        print "Training model for %s" % name
        model = models.LdaMulticore(corpus=corpus, iterations=50, chunksize=5000, num_topics=num_topics, id2word=dictionary, eval_every=3, workers=5)

        return SOQuestionTopicModel(name, model, dictionary, tokenizer)

    @staticmethod
    def load(name, tokenizer):
        print "Loading Dictionary and Model for %s" % name
        dictionary = corpora.Dictionary.load('output/%s.dict' % name)
        model = models.LdaModel.load("output/%s_model.lda" % name)
        return SOQuestionTopicModel(name, model, dictionary, tokenizer)

    def save(self):
        self.model.save("output/%s_model.lda" % self.name)

    def topics(self, text):
        return self.model[self._text_to_bow(self.tokenizer(text))]

    def _text_to_bow(self, text):
        return self.dictionary.doc2bow(text)


def vp_topic_model(name, load_from_file=False):
    chunker = TextChunker(stem_chunks=False)
    chunker.train()
    if load_from_file:
        return SOQuestionTopicModel.load(name, chunker.chunk_text)
    else:
        vp_model = SOQuestionTopicModel.train(name, chunker.chunk_text, load_corpus_from_file=True, num_topics=100, query_page_size=1000, subsample=0.2)
        vp_model.save()
        return vp_model


def complete_topic_model(name, load_from_file=False):
    if load_from_file:
        return SOQuestionTopicModel.load(name, utils.simple_preprocess)
    else:
        whole_model = SOQuestionTopicModel.train(whole_name, utils.simple_preprocess, load_corpus_from_file=True,
                                                 num_topics=150, query_page_size=1000, subsample=1.0)
        whole_model.save()
        return whole_model


if __name__ == "__main__":
    whole_name = "whole_question"
    vp_name = "VP_question"

    # complete_topic_model(vp_name, load_from_file=os.path.isfile("output/%s_model.lda" % whole_name))

    vp_topic_model(vp_name, load_from_file=os.path.isfile("output/%s_model.lda" % vp_name))
