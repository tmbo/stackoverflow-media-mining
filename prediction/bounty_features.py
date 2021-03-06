from ordereddict import OrderedDict
from time import time
from utils import trunc_log2, trunc_log10


# Write bounty features to console
def log(stats):
    print "Number of Answer: ", stats["num_answers"]
    print "Time since Question Creation: ", stats["time_till_bounty_creation"]
    print "Time since Question Creation(log): ", stats["log_time_till_bounty_creation"]
    print "Number of previous Bounties ", stats["num_old_bounties"]
    print "Bounty Height: ", stats["bounty_height"]
    print "Question Score: ", stats["question_score"]
    print "View Count: ", stats["view_count"]
    print "-----------------------------------------"


# Numbers of answers of a question
def number_of_answers(question):
    return question["answer_count"]


# Time between the creation date of a question and right now
def time_since_creation(question):
    creation_date = question["creation_date"]
    return time() - creation_date


# Assumed height of a bounty
def height_of_bounty(question):
    return 50


# Score of a question (upvotes - downvotes)
def score(question):
    return question["score"]


# Number of user visits on a question
def view_count(question):
    return question["view_count"]


# Combine all bounty features into a dictionary
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



