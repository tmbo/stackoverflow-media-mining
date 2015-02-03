from math import floor, log
import re
import os

TAG_RE = re.compile(r'<[^>]+>')
INLINE_CODE_RE = re.compile(r'`[^`]+`')
PRE_RE = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)


def remove_tags(text):
    return TAG_RE.sub('', text)


def remove_code(text):
    return INLINE_CODE_RE.sub('', CODE_RE.sub('', PRE_RE.sub('', text)))


def trunc_log10(value):
    if value == 0:
        return 0
    else:
        return int(floor(log(value, 10)))
    
    
def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def array_from_sparse(els, size):
    r = [0.0] * size
    for idx, value in els:
        r[idx] = value
    return r