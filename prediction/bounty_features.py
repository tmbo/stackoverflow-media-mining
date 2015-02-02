from time import time

def log(stats):

  print "Number of Answer: ", stats["num_answers"]
  print "Time since Question Creation: ", stats["time_since_creation"]
  print "Number of previous Bounties ", stats["num_old_bounties"]
  print "Bounty Height: ", stats["bounty_height"]
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



def calcBountyFeatures(question):

  stats = {
    "num_answers" : 0,
    "time_since_creation" : 0,
    "num_old_bounties" : 0,
    "bounty_height" : 0
  }

  stats["num_answers"] = numberOfAnswers(question)
  stats["time_since_creation"] = timeSinceCreation(question)
  stats["num_old_bounties"] = numberOfOldBounties(question)
  stats["bounty_height"] = heightOfBounty(question)

  return stats



