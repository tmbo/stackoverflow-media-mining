from __future__ import division
import itertools
from ordereddict import OrderedDict
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
    return reduce(lambda summed, x: summed + (1 if x[2] > threshold else 0), tag_stats, 0)


def tag_popularity(tag_stats):
    if len(tag_stats) == 0:
        return 0
    return reduce(lambda summed, x: summed + x[3], tag_stats, 0) / len(tag_stats)


def num_subscribers(subscribers, key):
    if len(subscribers) == 0:
        return 0
    return reduce(lambda summed, x: summed + (x[key] or 0), subscribers, 0) / len(subscribers)



def percentage_subscribers(subscribers, key):

    sum = 0
    count = 0
    for sub1 in subscribers: # active or responsive subscribers
        for sub2 in subscribers: # all subscribers
            if sub1[0] == sub2[0] and sub1[key] != None:
                sum += sub1[key] / sub2[1]
                count += 1

    if count == 0:
        return 0
    else:
        return sum / count


def min_subscribers(subscribers):
    if len(subscribers) == 0:
        return 0
    min_subscriber = min(subscribers, key=lambda x: x[1])
    return min_subscriber[1]


def max_subscribers(subscribers):
    if len(subscribers) == 0:
        return 0
    max_subscriber = max(subscribers, key=lambda x: x[1])
    return max_subscriber[1]


def tag_specificity(tags):
    # create the pair-wise combinations all tags and query DB for togetherness value
    if tags > 1:
        togetherness = 0
        for tagCombo in itertools.combinations(sorted(tags), 2):
            togetherness += query_togetherness(tagCombo)[0]
        return togetherness / len(tags)
    else:
        return 0


def calculate_tag_features(tags):
    tag_stats = query_tag_statistic("SO_TAGS", tags)
    tag_subscribers = query_tag_statistic("SO_TAG_SUBSCRIBERS", tags)

    stats = OrderedDict()

    stats["tag_popularity"] = tag_popularity(tag_stats)
    stats["tag_specificity"] = tag_specificity(tags)
    stats["num_pop_tags_25"] = number_of_popular_tags(tag_stats, 25)
    stats["num_pop_tags_50"] = number_of_popular_tags(tag_stats, 50)
    stats["num_pop_tags_100"] = number_of_popular_tags(tag_stats, 100)

    stats["num_subs_ans"] = num_subscribers(tag_subscribers, 2)
    stats["percent_subs_ans"] = percentage_subscribers(tag_subscribers, 2)
    stats["num_subs_t"] = num_subscribers(tag_subscribers, 3)
    stats["percent_subs_t"] = percentage_subscribers(tag_subscribers, 3)

    stats["log_min_tags_subs"] = trunc_log2(min_subscribers(tag_subscribers))
    stats["log_max_tags_subs"] = trunc_log2(max_subscribers(tag_subscribers))
    stats["log_tag_popularity"] = trunc_log2(stats["tag_popularity"])
    stats["log_tag_specificity"] = trunc_log10(stats["tag_specificity"])
    stats["log_num_subs_ans"] = trunc_log2(stats["num_subs_ans"])
    stats["log_percent_subs_ans"] = trunc_log2(stats["percent_subs_ans"])
    stats["log_num_subs_t"] = trunc_log2(stats["num_subs_t"])
    stats["log_percent_subs_t"] = trunc_log2(stats["percent_subs_t"])
    return stats


def query_togetherness(tag_combo):
    try:
        database = Database.from_config()
        connection, cursor = database.cursor()
        cursor.execute("SELECT togetherness FROM SO_TAG_COMBOS WHERE tag1=%s AND tag2=%s", tag_combo)
        result = cursor.fetchone()
        connection.close()
        return result
    except Exception as err:
        handle_connection_error(err)


def query_tag_statistic(table, tags):
    try:
        database = Database.from_config()
        connection, cursor = database.cursor()
        query = "SELECT * FROM %s WHERE " %table
        where_clause = " OR ".join(["Tag='%s'" % tag for tag in tags])
        query += where_clause

        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        return results

    except Exception as err:
        handle_connection_error(err)


def handle_connection_error(err):
    print("There was an error while communicating with the db. " + err.message)
