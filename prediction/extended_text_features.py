import ConfigParser
import mysql.connector
from mysql.connector import errorcode
from gensim import utils
from database import Database
from utils import removeTags, removeCode
from chunking import MultithreadedTextChunker
from operator import itemgetter
from text_statistics import TextStatistics
from train_lda import vp_topic_model, complete_topic_model
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def extract_best_topics(els, n):
    sorted_by_second = sorted(els, key=itemgetter(1), reverse=True)
    return map(itemgetter(0), sorted_by_second[0:n])


def updateTopicFeatures(data, cursor, writer):
    try:
        query = """UPDATE training_features, bounties b
            SET body_avg_chars=%s,
                body_avg_words=%s,
                body_ari=%s,
                body_cli=%s,
                body_fre=%s,
                body_gfi=%s,
                topics=%s,
                vp_topics=%s
            WHERE b.QuestionId=%s and b.Id = training_features.Id"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN UPDATE: "
        print err
        raise

if __name__ == "__main__":

    try:
        whole_name = "whole_question"
        vp_name = "VP_question"

        FlushSize = 500

        config = ConfigParser.RawConfigParser()
        config.read('application.cfg')

        cnx = Database(config).connection()

        print "Starting number crunching\n"

        cursor = cnx.cursor()
        cursor.execute("Select PostId, Body FROM bounty_text")

        # HACKY
        print "Fetching questions..."
        rows = cursor.fetchall()

        preprocessed_body = map(lambda row: removeTags(removeCode(row[1].encode("utf-8"))).lower(), rows)

        print "Loading models..."
        vp_model = vp_topic_model(vp_name,load_from_file=True)
        whole_model = complete_topic_model(whole_name, load_from_file=True)

        updateData = []

        for idx, row in enumerate(rows):
            whole_topics = whole_model.topics(preprocessed_body[idx])
            vp_topics = vp_model.topics(preprocessed_body[idx])

            data = []
            stats = TextStatistics(preprocessed_body)
            data.append(stats.avg_chars)
            data.append(stats.avg_words)
            data.append(stats.automated_readability_index())
            data.append(stats.coleman_liau_index())
            data.append(stats.flesch_reading_ease())
            data.append(stats.gunning_fog_index())
            data.append(str(whole_topics))
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


