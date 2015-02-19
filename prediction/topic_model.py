from gensim import utils, models, corpora
from database import Database
from chunking import TextChunker
import logging
import multiprocessing
from utils import *
from csv_reader import read_csv

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenizer = None


def _process_row(row):
    try:
        if row[1] is None:
            return row[0], []
        else:
            # return row[0], list(tokenizer(remove_tags(remove_code(row[1].encode("utf-8")))))
            return row[0], list(tokenizer(remove_tags(remove_code(row[1]))))
    except Exception as err:
        print "An exception occurred during processing of the row: "
        print row
        import traceback
        traceback.print_exc()
        
        

class SOQuestionCorpus(corpora.TextCorpus):
    def __init__(self, tokenizer, processes=None, query_page_size=50000, subsample=1.0, limit=None):
        self.tokenizer = tokenizer
        self.processes = processes
        self.subsample = subsample
        self.limit = limit
        self.query_page_size = query_page_size
        print "Creating dictionary..."
        super(SOQuestionCorpus, self).__init__(input=True)
        self.dictionary.filter_extremes(no_below=5, no_above=0.3)

    def get_texts(self):
        return self.question_body_stream()

    @staticmethod
    def pre_process(body):
        return remove_tags(remove_code(body))

    # def question_body_stream(self):
    #     global tokenizer
    #     tokenizer = self.tokenizer
    #     db = Database.from_config()
    #     query_results = db.paged_query(select="Body", from_="SO_POSTS", where="PostTypeId=1",
    #                                    page_size=self.query_page_size, subsample=self.subsample)
    #     pool = multiprocessing.Pool(self.processes)
    #     for page in query_results:
    #         for Id, tokens in pool.map(_process_row, page):
    #             if tokens:
    #                 yield tokens
    #             else:
    #                 print "ERROR in row %s" % Id
    #     pool.terminate()
    
    def question_body_stream(self):
        global tokenizer
        tokenizer = self.tokenizer
        csv = read_csv("output/stackoverflow-data/posts.csv", set(["Id", "Body"]), subsample=self.subsample, limit=self.limit)
        pool = multiprocessing.Pool(self.processes)
        for Id, tokens in pool.imap(_process_row, csv, chunksize=10000):
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
    def file_for_model(base_dir, name):
        return "%s/%s_model.lda" % (base_dir, name)

    @staticmethod
    def file_for_dict(base_dir, name):
        return "%s/%s.dict" % (base_dir, name)

    @staticmethod
    def file_for_corpus(base_dir, name):
        return "%s/%s.mm" % (base_dir, name)

    @staticmethod
    def train(name, base_dir, tokenizer, num_topics=100, load_corpus_from_file=False, query_page_size=50000,
              subsample=1.0, limit=None):
        if not load_corpus_from_file:
            corpus = SOQuestionCorpus(tokenizer, query_page_size=query_page_size, subsample=subsample, limit=limit)
            print "Storing corpus for %s name..." % name
            corpora.MmCorpus.serialize(SOQuestionTopicModel.file_for_corpus(base_dir, name), corpus, progress_cnt=10000)
            print "Storing dictionary for %s..." % name
            corpus.dictionary.save(SOQuestionTopicModel.file_for_dict(base_dir, name))

        corpus = corpora.MmCorpus(SOQuestionTopicModel.file_for_corpus(base_dir, name))
        dictionary = corpora.Dictionary.load(SOQuestionTopicModel.file_for_dict(base_dir, name))

        print "Training model for %s" % name
        model = models.LdaMulticore(corpus=corpus, iterations=50, chunksize=5000, num_topics=num_topics,
                                    id2word=dictionary, eval_every=3, workers=5)

        return SOQuestionTopicModel(name, model, dictionary, tokenizer)

    @staticmethod
    def load(name, base_dir, tokenizer):
        model_file_name = SOQuestionTopicModel.file_for_model(base_dir, name)
        dict_file_name = SOQuestionTopicModel.file_for_dict(base_dir, name)
        if os.path.isfile(model_file_name):
            print "Loading Dictionary and Model for %s" % name
            dictionary = corpora.Dictionary.load(dict_file_name)
            model = models.LdaModel.load(model_file_name)
            return SOQuestionTopicModel(name, model, dictionary, tokenizer)
        else:
            print "Tried to load Model from %s for %s, but FAILED" % (model_file_name, name)
            return None

    def save_model(self, base_dir):
        model_file_name = SOQuestionTopicModel.file_for_model(base_dir, self.name)
        self.model.save(model_file_name)

    def topics(self, text):
        return self.model[self._text_to_bow(self.tokenizer(text))]

    def _text_to_bow(self, text):
        return self.dictionary.doc2bow(text)


def vp_topic_model(name, base_dir="."):
    chunker = TextChunker(stem_chunks=True)
    chunker.train()
    model = SOQuestionTopicModel.load(name, base_dir, chunker.chunk_text)
    if model is None:
        model = SOQuestionTopicModel.train(
            name, base_dir, chunker.chunk_text, load_corpus_from_file=False, num_topics=100, query_page_size=1000,
            subsample=1, limit=10000)
        model.save_model(base_dir)
    return model


def complete_topic_model(name, base_dir="."):
    model = SOQuestionTopicModel.load(name, base_dir, utils.simple_preprocess)
    if model is None:
        model = SOQuestionTopicModel.train(whole_name, base_dir, utils.simple_preprocess, load_corpus_from_file=False,
                                           num_topics=150, query_page_size=1000, subsample=1.0)
        model.save(base_dir)
    return model


if __name__ == "__main__":
    base_dir = "output/ldas2"

    ensure_folder_exists(base_dir)

    whole_name = "whole_question"
    vp_name = "vp_question"

    # complete_topic_model(vp_name, base_dir)

    vp_topic_model(vp_name, base_dir)
