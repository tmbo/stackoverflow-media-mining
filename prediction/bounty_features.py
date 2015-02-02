from time import time
from utils import trunc_log10

def log(stats):

  print "Number of Answer: ", stats["num_answers"]
  print "Time since Question Creation: ", stats["time_till_bounty_creation"]
  print "Time since Question Creation(log): ", stats["log_time_till_bounty_creation"]
  print "Number of previous Bounties ", stats["num_old_bounties"]
  print "Bounty Height: ", stats["bounty_height"]
  print "Question Score: ", stats["question_score"]
  print "View Count: ", stats["view_count"]
  print "-----------------------------------------"


def numberOfAnswers(question):
  return question["answer_count"]


def timeSinceCreation(question):
  creationDate = question["creation_date"]
  timeDifference = time() - creationDate
  return timeDifference


def numberOfOldBounties(question):
  return 0


def heightOfBounty(question):
  return 50


def score(question):
  return question["score"]


def viewCount(question):
  return question["view_count"]


def calcBountyFeatures(question):

  stats = {}

  stats["num_answers"] = numberOfAnswers(question)
  stats["time_till_bounty_creation"] = timeSinceCreation(question)
  stats["log_time_till_bounty_creation"] = trunc_log10(stats["time_till_bounty_creation"])
  stats["num_old_bounties"] = numberOfOldBounties(question)
  stats["bounty_height"] = heightOfBounty(question)
  stats["question_score"] = score(question)
  stats["view_count"] = viewCount(question)

  return stats



