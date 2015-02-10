from database import Database
from operator import itemgetter
from text_statistics import TextStatistics
from utils import *
from topic_model import vp_topic_model, complete_topic_model
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FLUSH_LIMIT = 500

class TopicModel(object):

    def __init__(self):
        self.vp_model = vp_topic_model(name="vp_question", base_dir="output/ldas")
        self.whole_model = complete_topic_model(name="whole_question", base_dir="output/ldas")

    def predict_vp_topics(self, text):
        return self.vp_model.topics(text)


    def predict_whole_topics(self, text):
        return self.whole_model.topics(text)



def extract_best_topics(els, n):
    sorted_by_second = sorted(els, key=itemgetter(1), reverse=True)
    return map(itemgetter(0), sorted_by_second[0:n])


def update_topic_features(data, cursor, writer):
    try:
        query = """UPDATE SO_TRAINING_FEATURES
                    SET
                      body_avg_chars = ?,
                      body_avg_words = ?,
                      body_ari       = ?,
                      body_cli       = ?,
                      body_fre       = ?,
                      body_gfi       = ?,
                      topics         = ?,
                      vp_topics      = ?
                    WHERE
                      Id = ?"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN UPDATE: "
        print err
        raise

if __name__ == "__main__":

    try:
        cnx = Database.from_config().connection()

        print "Starting number crunching\n"

        cursor = cnx.cursor()
        cursor.execute("""SELECT
                            b.Id,
                            question.Body
                          FROM SO_BOUNTIES b, SO_POSTS question
                          WHERE
                            b.QuestionId = question.Id""")

        print "Fetching questions..."
        rows = cursor.fetchall()

        preprocessed_body = map(lambda row: remove_tags(remove_code(row[1].encode("utf-8"))).lower(), rows)

        print "Loading models..."
        vp_model = vp_topic_model(name="vp_question", base_dir="output/ldas")
        whole_model = complete_topic_model(name="whole_question", base_dir="output/ldas")

        updateData = []

        for idx, row in enumerate(rows):
            whole_topics = whole_model.topics(preprocessed_body[idx])
            vp_topics = vp_model.topics(preprocessed_body[idx])

            data = []
            stats = TextStatistics(preprocessed_body)
            data.append(stats.avg_chars())
            data.append(stats.avg_words())
            data.append(stats.automated_readability_index())
            data.append(stats.coleman_liau_index())
            data.append(stats.flesch_reading_ease())
            data.append(stats.gunning_fog_index())
            data.append(str(whole_topics))
            data.append(str(vp_topics))
            data.append(row[0])
            updateData.append(data)
            if len(updateData) > FLUSH_LIMIT:
                update_topic_features(updateData, cursor, cnx)
                updateData = []
                print "Finished %d" % idx

        if len(updateData) > 0:
            update_topic_features(updateData, cursor, cnx)

        print "Done"

    except Exception as err:
            print("An exception occoured: " + err)
    else:
        cnx.close()


