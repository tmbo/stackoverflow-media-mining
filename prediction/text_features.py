from ordereddict import OrderedDict
from database import Database
from utils import *
import re

CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)
IMG_RE = re.compile(r'<img (.*?)/?>', re.DOTALL)
SELF_RE = re.compile(r'I(?=\')|I(?=\s)|we(?=\s)|me(?=\s)|myself(?=\s)|our(?=\s)', re.IGNORECASE)
VERBS_RE = re.compile(r'run(?=\s)|tried(?=\s)|did(?=\s)|made(?=\s)|used(?=\s)|tested(?=\s)')

# Differentite between small inline code examples and long blocks of code
CODE_SAMPLE_THRESHOLD = 10


def number_of_code_snippets(text):
    # How many code snippets does the post contain.
    snippets = CODE_RE.findall(text)
    # exclude tiny inline code snippets
    return len(filter(lambda x: len(x) >= CODE_SAMPLE_THRESHOLD, snippets))


def number_of_images(text):
    # How many images does the post contain.
    snippets = IMG_RE.findall(text)
    return len(snippets)


def length_of_code_snippets(text):
    # Overall length of all code snippets combined
    snippets = CODE_RE.findall(text)
    # exclude tiny inline code snippets
    return reduce(lambda summed, x: summed + len(x), snippets, 0)


def text_length(text):
    return len(text.strip())


def ends_with_question_mark(text):
    # Does the title end with a question mark?
    # return an Int instead of Bool; SVM only understands numbers
    return int(text[-1] == "?")


def starts_with_question_word(text):
    # String starts with question words like "What", "Why", "Who", "How" ...
    # return an Int instead of Bool; SVM only understands numbers
    condition = text[:2].lower() == "wh" or text[:3].lower() == "how"
    return int(condition)


def number_of_self_ref(text):
    # Number of self reference like "I", "myself", "we", "our"...
    return len(SELF_RE.findall(text))


def number_of_action_verbs(text):
    # Number of action verbs like "tried", "run", "did", "made"...
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
    stats = OrderedDict()

    # calculate all code-based features with HTML tags still intact
    stats["num_code_snippet"] = number_of_code_snippets(body)
    stats["num_images"] = number_of_images(body)
    stats["code_len"] = length_of_code_snippets(body)

    # remove all outer HTML tags
    body = remove_tags(remove_code(body))

    # body features
    stats["body_len"] = text_length(body)
    stats["num_selfref"] = number_of_self_ref(body)
    stats["num_active_verb"] = number_of_action_verbs(body)

    # title features
    stats["title_len"] = text_length(title)
    stats["end_que_mark"] = ends_with_question_mark(title)
    stats["begin_que_word"] = starts_with_question_word(title)

    stats["log_body_len"] = trunc_log2(stats["body_len"])
    stats["log_code_len"] = trunc_log2(stats["code_len"])
    stats["log_code_snippets"] = trunc_log2(stats["num_code_snippet"])
    stats["log_selfref"] = trunc_log2(stats["num_selfref"])
    stats["log_active_verb"] = trunc_log2(stats["num_active_verb"])
    #stats["log_code_len"] = trunc_log2(stats["code_len"])
    return stats
