from gensim import models
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# This file is mostly for debug purposes
# It can be used to print the topics of an LDA model
# to console.

if __name__ == "__main__":
    # Prints a lda model to console
    name = "VP_question"
    # name = "whole_question"

    lda_model = models.LdaModel.load("output/%s_model.lda" % name)

    lda_model.print_topics(num_topics=150, num_words=10)