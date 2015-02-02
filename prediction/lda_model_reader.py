from gensim import utils, models, corpora
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

name = "VP_question"
# name = "whole_question"

lda_model = models.LdaModel.load("output/%s_model.lda" % name)

lda_model.print_topics(num_topics=150, num_words=10)