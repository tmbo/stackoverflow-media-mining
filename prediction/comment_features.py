from utils import *

def log(stats):

  print "Number of Comments: ", stats["num_comments"]
  print "Toal Comment Length: ", stats["comment_len"]
  print "Average Comment Length: ", stats["avg_comment_len"]
  print "-----------------------------------------"


def numberOfComments(comments):
  return len(comments)


def commentLength(comments):
  lengths = map(lambda x: len(removeTags(x["body"])), comments)
  return reduce(lambda sum, x: sum + x ,lengths , 0)


def averageCommentLength(commentLength, numComments):
  if numComments == 0:
    return 0
  else:
    return commentLength / numComments


def calcCommentFeatures(comments):

  stats = {}

  stats["num_comments"] = numberOfComments(comments)
  stats["comment_len"] = commentLength(comments)
  stats["avg_comment_len"] = averageCommentLength(stats["comment_len"], stats["num_comments"])
  stats["log_num_comments"] = trunc_log10(stats["num_comments"])
  stats["log_comment_len"] = trunc_log10(stats["comment_len"])

  return stats



