import re

TAG_RE = re.compile(r'<[^>]+>')


def removeTags(text):
    return TAG_RE.sub('', text)


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


def calcCommentFeatures(comments):

  stats = {
    "num_comments" : 0,
    "comment_len" : 0,
    "avg_comment_len" : 0,
  }

  stats["num_comments"] = numberOfComments(comments)
  stats["comment_len"] = commentLength(comments)
  stats["avg_comment_len"] =   stats["comment_len"] / stats["num_comments"]

  return stats



