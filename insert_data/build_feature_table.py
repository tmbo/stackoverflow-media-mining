import re, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'prediction')) #find modules in parent_folder/predictions
from database import Database
import text_features
import tag_features
import comment_features
import bounty_features
from sklearn.externals import joblib
from extended_text_features import TopicModel
from text_statistics import TextStatistics

TAG_EXTRACTOR = re.compile(r'<([^>]+)>')


if __name__ == "__main__":

  db = Database.from_config()
  for rows in db.paged_query(
    select="B.ID, BODY, TITLE, TAGS",
    from_="SO_BOUNTIES AS B, SO_POSTS AS P",
    where="B.QuestionID = P.ID"):

    for row in rows:

      id = row[0],
      body = row[1],
      title = row[2]

      processed_body = remove_tags(remove_code(question["body"]))
      processed_tags = TAG_EXTRACTOR.findall(tag_string)

      features = OrderedDict()
      features["textFeatures"] = text_features.calculate_text_features(body, title)
      features["tagFeatures"] = tag_features.calculate_tag_features(process_tags)
      features["bountyFeatures"] = bounty_features.calculate_bounty_features(question)
      features["commentFeatures"] = comment_features.calculate_comment_features(comments)
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