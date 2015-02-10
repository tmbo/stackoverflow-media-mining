from ordereddict import OrderedDict
from time import time
from utils import trunc_log2, trunc_log10


def log(stats):
    print "Number of Answer: ", stats["num_answers"]
    print "Time since Question Creation: ", stats["time_till_bounty_creation"]
    print "Time since Question Creation(log): ", stats["log_time_till_bounty_creation"]
    print "Number of previous Bounties ", stats["num_old_bounties"]
    print "Bounty Height: ", stats["bounty_height"]
    print "Question Score: ", stats["question_score"]
    print "View Count: ", stats["view_count"]
    print "-----------------------------------------"


def number_of_answers(question):
    return question["answer_count"]


def time_since_creation(question):
    creation_date = question["creation_date"]
    return time() - creation_date


def height_of_bounty(question):
    return 50


def score(question):
    return question["score"]


def view_count(question):
    return question["view_count"]


def calculate_bounty_features(question):
    stats = OrderedDict()

    stats["bounty_height"] = height_of_bounty(question)
    stats["num_answers"] = number_of_answers(question)
    stats["time_till_bounty_creation"] = time_since_creation(question)
    stats["log_time_till_bounty_creation"] = trunc_log2(stats["time_till_bounty_creation"])
    stats["question_score"] = score(question)
    stats["view_count"] = view_count(question)
    stats["log_avg_daily_view"] = trunc_log10(stats["view_count"] / stats["time_till_bounty_creation"])

    stats["other_active_bounties"] = 0  # TODO remove this one

    stats["log_num_answers"] = trunc_log2(stats["num_answers"])
    stats["log_view_count"] = trunc_log2(stats["view_count"])

    stats["log_other_bounties"] = 0  # TODO remove this one

    return stats



