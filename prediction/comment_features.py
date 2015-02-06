from utils import *


def log(stats):
    print "Number of Comments: ", stats["num_comments"]
    print "Toal Comment Length: ", stats["comment_len"]
    print "Average Comment Length: ", stats["avg_comment_len"]
    print "-----------------------------------------"


def number_of_comments(comments):
    return len(comments)


def length_of_comments(comments):
    return sum(map(lambda x: len(remove_tags(x["body"])), comments), 0)


def average_comment_length(comment_length, num_comments):
    return (comment_length / num_comments) if num_comments != 0 else 0


def calculate_comment_features(comments):
    stats = dict()

    stats["num_comments"] = number_of_comments(comments)
    stats["comment_len"] = length_of_comments(comments)
    stats["avg_comment_len"] = average_comment_length(stats["comment_len"], stats["num_comments"])
    stats["log_num_comments"] = trunc_log2(stats["num_comments"])
    stats["log_comment_len"] = trunc_log2(stats["comment_len"])

    return stats



