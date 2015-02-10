from collections import OrderedDict
import re, sys, os
from database import Database
from prediction.text_features import *
from prediction.tag_features import *
from prediction.comment_features import *
from sklearn.externals import joblib
from prediction.extended_text_features import TopicModel
from prediction.text_statistics import TextStatistics

TAG_EXTRACTOR = re.compile(r'<([^>]+)>')


if __name__ == "__main__":

  db = Database.from_config()
  for rows in db.paged_query(
    select="BODY, TITLE, TAGS",
    from_="SO_BOUNTIES AS B, SO_POSTS AS P",
    where="B.QuestionID = P.ID",
    id_prefix="B"):

    for row in rows:

      id = row[0]
      body = row[1]
      title = row[2]
      tag_string = row[3]

      processed_body = remove_tags(remove_code(body))
      processed_tags = TAG_EXTRACTOR.findall(tag_string)

      features = OrderedDict()
      features["textFeatures"] = calculate_text_features(body, title)
      features["tagFeatures"] = calculate_tag_features(processed_tags)
      features["commentFeatures"] = calculate_comment_features(comments)
      features["shallowLinguisticFeatures"] = TextStatistics(processed_body).calculate_shallow_text_features()

      print features

      values = []
      for category, feature in features.items():
        for value in feature.values():
          if isinstance(value, list):
            values.extend(value) # arrays
          else:
            values.append(value) # single Integers, Floats

      # UPDATE(values)