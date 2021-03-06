from math import floor, log
import re
import os
import itertools

TAG_RE = re.compile(r'<[^>]+>')
INLINE_CODE_RE = re.compile(r'`[^`]+`')
PRE_RE = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)
LF_RE = re.compile(r'&#xA;')


def _ctoi(c):
    if type(c) == type(""):
        return ord(c)
    else:
        return c


def isdigit(c): 
    return 57 >= _ctoi(c) >= 48 


def remove_tags(text):
    return LF_RE.sub(' ', TAG_RE.sub('', text))


def remove_code(text):
    return INLINE_CODE_RE.sub('', CODE_RE.sub('', PRE_RE.sub('', text)))


def trunc_log10(value):
    if value == 0:
        return 0
    else:
        return int(floor(log(value, 10)))


def trunc_log2(value):
    if value == 0:
        return 0
    else:
        return int(floor(log(value, 2)))


def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def array_from_sparse(els, size):
    r = [0.0] * size
    for idx, value in els:
        r[idx] = value
    return r

def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk