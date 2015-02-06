from database import Database
from operator import itemgetter
from text_statistics import TextStatistics
from utils import *
from topic_model import vp_topic_model, complete_topic_model
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FLUSH_LIMIT = 500


def extract_best_topics(els, n):
    sorted_by_second = sorted(els, key=itemgetter(1), reverse=True)
    return map(itemgetter(0), sorted_by_second[0:n])


def update_topic_features(data, cursor, writer):
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
        cnx = Database.from_config().connection()

        print "Starting number crunching\n"

        cursor = cnx.cursor()
        cursor.execute("Select PostId, Body FROM bounty_text")

        print "Fetching questions..."
        rows = cursor.fetchall()

        preprocessed_body = map(lambda row: remove_tags(remove_code(row[1].encode("utf-8"))).lower(), rows)

        print "Loading models..."
        vp_model = vp_topic_model(name="whole_question", base_dir="../output/ldas")
        whole_model = complete_topic_model(name="vp_question", base_dir="../output/ldas")

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

