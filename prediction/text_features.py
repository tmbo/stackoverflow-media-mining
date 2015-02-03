from database import Database
from utils import *
import re

CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)
IMG_RE = re.compile(r'<img (.*?)/?>', re.DOTALL)
SELF_RE = re.compile(r'I(?=\')|I(?=\s)|we(?=\s)|me(?=\s)|myself(?=\s)|our(?=\s)', re.IGNORECASE)
VERBS_RE = re.compile(r'run(?=\s)|tried(?=\s)|did(?=\s)|made(?=\s)|used(?=\s)|tested(?=\s)')

CODE_SAMPLE_THRESHOLD = 10


def contains_code_sample(text):
    return number_of_code_snippets(text) > 0


def number_of_code_snippets(text):
    snippets = CODE_RE.findall(text)
    # exclude tiny inline code snippets
    return len(filter(lambda x: len(x) >= CODE_SAMPLE_THRESHOLD, snippets))


def number_of_images(text):
    snippets = IMG_RE.findall(text)
    return len(snippets)


def length_of_code_snippets(text):
    snippets = CODE_RE.findall(text)
    # exclude tiny inline code snippets
    return reduce(lambda summed, x: summed + len(x), snippets, 0)


def text_length(text):
    return len(text.strip())


def ends_with_question_mark(text):
    return text[-1] == "?"


def starts_with_question_word(text):
    # String starts with question words like "What", "Why", "Who", "How" ...
    return text[:2].lower() == "wh" or text[:3].lower() == "how"


def number_of_self_ref(text):
    return len(SELF_RE.findall(text))


def number_of_action_verbs(text):
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


def calculate_text_features(postId, body, title):
    stats = dict()

    # calculate all code-based features with HTML tags still intact
    stats["num_code_snippet"] = number_of_code_snippets(body)
    stats["code_len"] = length_of_code_snippets(body)
    stats["num_images"] = number_of_images(body)
    stats["log_code_snippet"] = trunc_log10(stats["num_code_snippet"])
    stats["log_code_len"] = trunc_log10(stats["code_len"])

    # remove all outer HTML tags
    body = remove_tags(remove_code(body))

    # body features
    stats["body_len"] = text_length(body)
    stats["num_selfref"] = number_of_self_ref(body)
    stats["num_active_verb"] = number_of_action_verbs(body)
    stats["log_body_len"] = trunc_log10(stats["body_len"])
    stats["log_selfref"] = trunc_log10(stats["num_selfref"])
    stats["log_active_verb"] = trunc_log10(stats["num_active_verb"])

    # title features
    stats["title_len"] = text_length(title)
    stats["end_que_mark"] = ends_with_question_mark(title)
    stats["begin_que_word"] = starts_with_question_word(title)

    return stats


def update_db(stats, cursor, cnx):
    cursor.execute("""
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
  """, (stats["num_code_snippet"], stats["num_images"], stats["code_len"], stats["body_len"], stats["title_len"],
        stats["end_que_mark"], stats["begin_que_word"], stats["num_selfref"], stats["num_active_verb"],
        stats["postId"]))
    cnx.commit()


# ========= Main Entry Point ============
#
# Only run this Script manually when trying to batch calculate features from DB
#
if __name__ == "__main__":

    try:
        cnx = Database.from_config()

        print "Starting number crunching\n"

        cursor = cnx.cursor()
        cursor.execute("Select * FROM bounty_text")
        rows = cursor.fetchall()

        for row in rows:
            # Python uses ASCII by default?
            body = row[2].encode("utf-8")
            postId = row[1]
            title = row[4]

            stats = calculate_text_features(postId, body, title)

            update_db(stats, cursor, cnx)
            log(stats)

        print "Done"

    except Exception as err:
        print("There was an error while communicating with the db. " + err)
    else:
        cnx.close()
