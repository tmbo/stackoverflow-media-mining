import mysql.connector
from mysql.connector import errorcode
from utils import *
import re

CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)
IMG_RE = re.compile(r'<img (.*?)/?>', re.DOTALL)
SELF_RE = re.compile(r'I(?=\')|I(?=\s)|we(?=\s)|me(?=\s)|myself(?=\s)|our(?=\s)', re.IGNORECASE)
VERBS_RE = re.compile(r'run(?=\s)|tried(?=\s)|did(?=\s)|made(?=\s)|used(?=\s)|tested(?=\s)')

CODE_SAMPLE_THRESHOLD = 10

def containsCodeSample(text):
  return len(number_of_code_snippets(text)) > 0


def number_of_code_snippets(text):
  snippets = CODE_RE.findall(text)
  # exclude tiny inline code snippets
  return len(filter(lambda x: len(x) >= CODE_SAMPLE_THRESHOLD, snippets))

def numberOfImages(text):
  snippets = IMG_RE.findall(text)
  return len(snippets)


def lengthOfCodeSnippets(text):
  snippets = CODE_RE.findall(text)
  # exclude tiny inline code snippets
  return reduce(lambda sum, x: sum + len(x), snippets, 0)


def textLength(text):
  return len(text.strip())


def endsWithQuestionMark(text):
  return text[-1] == "?"


def startsWithQuestionWord(text):
  # String starts with question words like "What", "Why", "Who", "How" ...
  return text[:2].lower() == "wh" or text[:3].lower() == "how"


def numberOfSelfRef(text):
  return len(SELF_RE.findall(text))


def numberOfActionVerbs(text):
  return len(VERBS_RE.findall(text))


def log(stats):

  print "PostID: ", stats["postId"]
  print "Number of Code Snippets : ", stats["num_code_snippet"]
  print "Number of Images: ", stats["num_images"]
  print "Total Length of Code : ", stats["code_len"]
  print "Length of Body: ", stats["body_len"]
  print "Number of self ref words: ", stats["num_selfref"]
  print "Number of action words: ", stats["num_active_verb"]
  print "Length of Title: ", stats["title_len"]
  print "Title ends with ?: ", stats["end_que_mark"]
  print "Title starts with question word: ", stats["begin_que_word"]
  print "-----------------------------------------"


def calcTextFeatures(postId, body, title):

  stats = {}

  #calculate all code-based features with HTML tags still intact
  stats["num_code_snippet"] = number_of_code_snippets(body)
  stats["code_len"] = lengthOfCodeSnippets(body)
  stats["num_images"] = numberOfImages(body)
  stats["log_code_snippet"] = trunc_log10(stats["num_code_snippet"])
  stats["log_code_len"] = trunc_log10(stats["code_len"])

  # remove all outer HTML tags
  body = removeTags(removeCode(body))

  # body features
  stats["body_len"] = textLength(body)
  stats["num_selfref"] = numberOfSelfRef(body)
  stats["num_active_verb"] = numberOfActionVerbs(body)
  stats["log_body_len"] = trunc_log10(stats["body_len"])
  stats["log_selfref"] = trunc_log10(stats["num_selfref"])
  stats["log_active_verb"] = trunc_log10(stats["num_active_verb"])

  # title features
  stats["title_len"] = textLength(title)
  stats["end_que_mark"] = endsWithQuestionMark(title)
  stats["begin_que_word"] = startsWithQuestionWord(title)

  return stats

def updateDB(stats):
  rows_affected = cursor.execute("""
UPDATE bounty_text
SET
  num_code_snippet=%s,
  num_images=%s,
  code_len=%s,
  body_len=%s,
  title_len=%s,
  end_que_mark=%s,
  begin_que_word=%s,
  num_selfref=%s,
  num_active_verb=%s
WHERE PostId=%s
  """,  (stats["num_code_snippet"], stats["num_images"], stats["code_len"], stats["body_len"], stats["title_len"], stats["end_que_mark"], stats["begin_que_word"], stats["num_selfref"], stats["num_active_verb"], stats["postId"]))
  cnx.commit()


# ========= Main Entry Point ============
#
# Only run this Script manually when trying to batch calculate features from DB
#
if __name__ == "__main__":

  try:

    cnx = mysql.connector.connect(user="root",
                                  database="stackoverflow",
                                  host="localhost")

    print "Starting number crunching\n"

    cursor = cnx.cursor()
    cursor.execute("Select * FROM bounty_text")


    # HACKY
    rows = cursor.fetchall()

    for row in rows:

      # Python uses ASCII by default?
      body = row[2].encode("utf-8")
      postId = row[1]
      title = row[4]

      stats = calcTextFeatures(postId, body, title)

      updateDB(stats)
      log(stats)

    print "Done"

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exists")
    else:
      print(err)
  else:
    cnx.close()

