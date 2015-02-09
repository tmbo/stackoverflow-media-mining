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
    return reduce(lambda summed, x: summed + (1 if x["Count"] > threshold else 0), tag_stats, 0)


def tag_popularity(tag_stats):
    return reduce(lambda summed, x: summed + x["Freq"], tag_stats, 0) / len(tag_stats)


def num_subscribers(tag_subscribers):
    return reduce(lambda summed, x: summed + x["NumberOfUsers"], tag_subscribers, 0) / len(tag_subscribers)


def percentage_subscribers(active_subscribers, all_subscribers):
    sum = 0
    for i in range(0, len(active_subscribers)):
        print active_subscribers[i]["Tag"]
        print all_subscribers[i]["Tag"]
        sum += active_subscribers[i]["NumberOfUsers"] / all_subscribers[i]["NumberOfUsers"]

    return sum / len(active_subscribers)
    # sum_all_subscribers = num_subscribers(all_subscribers)
    # print sum_all_subscribers
    # return active_subscribers / sum_all_subscribers


def min_subscribers(all_subscribers):
    min_subscriber = min(all_subscribers, key=lambda x: x["NumberOfUsers"])
    return min_subscriber["NumberOfUsers"]


def max_subscribers(all_subscribers):
    max_subscriber = max(all_subscribers, key=lambda x: x["NumberOfUsers"])
    return max_subscriber["NumberOfUsers"]


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
    tag_stats = query_tag_statistic("tags", tags)
    tag_responsive_subscribers = query_tag_statistic("subscribers_responsive", tags)
    tag_active_subscribers = query_tag_statistic("subscribers_active", tags)
    tag_all_subscribers = query_tag_statistic("subscribers_all", tags)

    stats = OrderedDict()

    stats["tag_popularity"] = tag_popularity(tag_stats)
    stats["tag_specificity"] = tag_specificity(tags)
    stats["num_pop_tags_25"] = number_of_popular_tags(tag_stats, 25)
    stats["num_pop_tags_50"] = number_of_popular_tags(tag_stats, 50)
    stats["num_pop_tags_100"] = number_of_popular_tags(tag_stats, 100)

    stats["num_subs_ans"] = num_subscribers(tag_active_subscribers)
    stats["percent_subs_ans"] = percentage_subscribers(tag_active_subscribers, tag_all_subscribers)
    stats["num_subs_t"] = num_subscribers(tag_responsive_subscribers)
    stats["percent_subs_t"] = percentage_subscribers(tag_responsive_subscribers, tag_all_subscribers)

    stats["log_min_tags_subs"] = trunc_log2(min_subscribers(tag_all_subscribers))
    stats["log_max_tags_subs"] = trunc_log2(max_subscribers(tag_all_subscribers))
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
        connection, cursor = database.cursor(dictionary=True)
        cursor.execute("SELECT togetherness FROM tag_combos WHERE tag1=%s AND tag2=%s", tag_combo)
        result = cursor.fetchone()
        connection.close()
        return result
    except Exception as err:
        handle_connection_error(err)


def query_tag_statistic(table, tags):
    try:
        database = Database.from_config()
        connection, cursor = database.cursor(dictionary=True)
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
