from ordereddict import OrderedDict
import re, sys, os
from prediction.database import Database
from prediction.text_features import *
from prediction.tag_features import *
from prediction.comment_features import *
from sklearn.externals import joblib
from prediction.extended_text_features import TopicModel
from prediction.text_statistics import TextStatistics

TAG_EXTRACTOR = re.compile(r'<([^>]+)>')
FLUSH_LIMIT = 500

def update_trainings_features(data, cursor, writer):

    try:
        query = """UPDATE SO_TRAINING_FEATURES
                    SET
                    num_code_snippet = ?,
                    num_images = ?,
                    code_len = ?,
                    body_len = ?,
                    num_selfref = ?,
                    num_active_verb = ?,
                    title_len = ?,
                    end_que_mark = ?,
                    begin_que_word = ?,
                    log_body_len = ?,
                    log_code_len = ?,
                    log_code_snippets = ?,
                    log_selfref = ?,
                    log_active_verb = ?,
                    tag_popularity = ?,
                    tag_specificity = ?,
                    num_pop_tags_25 = ?,
                    num_pop_tags_50 = ?,
                    num_pop_tags_100 = ?,
                    num_subs_ans = ?,
                    percent_subs_ans = ?,
                    num_subs_t = ?,
                    percent_subs_t = ?,
                    log_min_tag_subs = ?,
                    log_max_tag_subs = ?,
                    log_tag_popularity = ?,
                    log_tag_specifity = ?,
                    log_num_subs_ans = ?,
                    log_percent_subs_ans = ?,
                    log_num_subs_t = ?,
                    log_percent_subs_t = ?,
                    body_ari = ?,
                    body_cli = ?,
                    body_fre = ?,
                    body_gfi = ?,
                    body_avg_chars = ?,
                    body_avg_words = ?,
                    log_body_ari = ?,
                    log_body_cli = ?,
                    log_body_fre = ?,
                    log_body_gfi = ?,
                    log_avg_words = ?
                    WHERE
                      Id = ?"""
        cursor.executemany(query, data)
        print cursor.statement
        writer.commit()
    except Exception as err:
        print "ERROR IN UPDATE: "
        print err
        raise

if __name__ == "__main__":

  db = Database.from_config()
  cnx = db.connection()
  cursor = cnx.cursor()

  updateData = []

  for rows in db.paged_query(
    select="BODY, TITLE, TAGS",
    from_="SO_BOUNTIES AS B, SO_POSTS AS P",
    where="B.QuestionID = P.ID",
    id_prefix="B",
    page_size=5000):

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
      features["shallowLinguisticFeatures"] = TextStatistics(processed_body).calculate_shallow_text_features()

      # convert ordereddicts to list
      values = []
      for category, feature in features.items():
        for value in feature.values():
          if isinstance(value, list):
            values.extend(value) # arrays
          else:
            values.append(value) # single Integers, Floats
      values.append(id)


      updateData.append(values)

      if len(updateData) > FLUSH_LIMIT:
        update_trainings_features(updateData, cursor, cnx)
        updateData = []

