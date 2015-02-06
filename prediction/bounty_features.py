from time import time
from utils import trunc_log2


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


def number_of_old_bounties(question):
    return 0


def height_of_bounty(question):
    return 50


def score(question):
    return question["score"]


def view_count(question):
    return question["view_count"]


def calculate_bounty_features(question):
    stats = dict()

    stats["num_answers"] = number_of_answers(question)
    stats["time_till_bounty_creation"] = time_since_creation(question)
    stats["log_time_till_bounty_creation"] = trunc_log2(stats["time_till_bounty_creation"])
    stats["num_old_bounties"] = number_of_old_bounties(question)
    stats["bounty_height"] = height_of_bounty(question)
    stats["question_score"] = score(question)
    stats["view_count"] = view_count(question)

    return stats



