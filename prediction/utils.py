from math import floor, log
import re

TAG_RE = re.compile(r'<[^>]+>')
INLINE_CODE_RE = re.compile(r'`[^`]+`')
PRE_RE = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
CODE_RE = re.compile(r'<code>(.*?)</code>', re.DOTALL)


def removeTags(text):
    return TAG_RE.sub('', text)


def removeCode(text):
  return INLINE_CODE_RE.sub('', CODE_RE.sub('', PRE_RE.sub('', text)))


def trunc_log10(value):
  if value == 0:
    return 0
  else:
    return int(floor(log(value, 10)))