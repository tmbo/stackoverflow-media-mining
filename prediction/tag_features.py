import itertools
from database import Database
from utils import *


def log(stats):
    print "Average frequency of Tags : ", stats["tag_popularity"]
    print "Number of Popular Tags (25): ", stats["num_pop_tags_25"]
    print "Number of Popular Tags (50): ", stats["num_pop_tags_50"]
    print "Number of Popular Tags (100): ", stats["num_pop_tags_100"]
    print "Average co-occurance of Tags: ", stats["tag_specificity"]
    print "-----------------------------------------"


def number_of_popular_tags(tag_stats, threshold):
    return reduce(lambda summed, x: summed + (1 if x["Count"] > threshold else 0), tag_stats, 0)


def tag_popularity(tag_stats):
    return reduce(lambda summed, x: summed + x["Freq"], tag_stats, 0) / len(tag_stats)


def tag_specificity(tags):
    # create the pair-wise combinations all tags and query DB for togetherness value
    if tags > 1:
        togetherness = 0
        for tagCombo in itertools.combinations(sorted(tags), 2):
            togetherness += query_togetherness(tagCombo)["togetherness"]
        return togetherness / len(tags)
    else:
        return 0


def calculate_tag_features(tags):
    tag_stats = query_tag_statistic(tags)

    stats = dict()

    stats["num_pop_tags_25"] = number_of_popular_tags(tag_stats, 25)
    stats["num_pop_tags_50"] = number_of_popular_tags(tag_stats, 50)
    stats["num_pop_tags_100"] = number_of_popular_tags(tag_stats, 100)
    stats["tag_popularity"] = tag_popularity(tag_stats)
    stats["tag_specificity"] = tag_specificity(tags)
    stats["log_tag_specificity"] = trunc_log10(stats["tag_specificity"])
    stats["log_tag_popularity"] = trunc_log10(stats["tag_popularity"])
    stats["log_tag_specificity"] = trunc_log10(stats["tag_specificity"])

    return stats


def query_togetherness(tag_combo):
    try:
        database = Database.from_config()
        connection, cursor = database.cursor(dictionary=True)
        cursor.execute("SELECT togetherness FROM tag_combos WHERE tag1=%s AND tag2=%s", tag_combo)
        result = cursor.fetchone()
        connection.close()
        return result
    except Exception as err:
        handle_connection_error(err)


def query_tag_statistic(tags):
    try:
        database = Database.from_config()
        connection, cursor = database.cursor(dictionary=True)
        query = "SELECT * FROM tags WHERE "
        where_clause = " OR ".join(["Tag='%s'" % tag for tag in tags])
        query += where_clause

        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        return results

    except Exception as err:
        handle_connection_error(err)


def handle_connection_error(err):
    print("There was an error while communicating with the db. " + err)
