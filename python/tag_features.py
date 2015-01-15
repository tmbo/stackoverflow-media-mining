import mysql.connector
from mysql.connector import errorcode
import itertools

user="root"
database="stackoverflow"
host="localhost"

def log(stats):

  print "PostID: ", stats["postId"]
  print "Average frequency of Tags : ", stats["tag_popularity"]
  print "Number of Popular Tags (25): ", stats["num_pop_tags_25"]
  print "Number of Popular Tags (50): ", stats["num_pop_tags_50"]
  print "Number of Popular Tags (100): ", stats["num_pop_tags_100"]
  print "Average co-occurance of Tags: ", stats["tag_specificity"]
  print "-----------------------------------------"


def numberOfPopularTags(tagStats, threshold):
  return reduce(lambda sum, x: sum + (1 if x["Count"] > threshold else 0),tagStats , 0)


def tagPopularity(tagStats):
  return reduce(lambda sum, x: sum + x["Freq"] ,tagStats , 0) / len(tagStats)


def tagSpecificity(tags):
  # create the pair-wise combinations all tags and query DB for togetherness value
  if tags > 1:
    togetherness = 0
    for tagCombo in itertools.combinations(sorted(tags), 2):
      togetherness += queryTogetherness(tagCombo)["togetherness"]
    return togetherness / len(tags)
  else:
    return 0


def calcTagFeatures(postId, tags):

  tagStats = queryTagStatistic(tags)

  stats = {
    "postId" : postId,
    "tag_popularity" : 0,
    "tag_specificity" : 0,
    "num_pop_tags_25" : 0,
    "num_pop_tags_50" : 0,
    "num_pop_tags_100" : 0,
  }

  stats["num_pop_tags_25"] = numberOfPopularTags(tagStats, 25)
  stats["num_pop_tags_50"] = numberOfPopularTags(tagStats, 50)
  stats["num_pop_tags_100"] = numberOfPopularTags(tagStats, 100)
  stats["tag_popularity"] = tagPopularity(tagStats)
  stats["tag_specificity"] = tagSpecificity(tags)

  return stats


def queryTogetherness(tagCombo):

  try:
    cnx = mysql.connector.connect(user=user, database=database, host=host)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT togetherness FROM tag_combos WHERE tag1=%s AND tag2=%s", tagCombo)
    return cursor.fetchone()

  except mysql.connector.Error as err:
    handleConnectionError(err)
  else:
    cnx.close()


# ========= Main Entry Point ============
def queryTagStatistic(tags):

  try:
    cnx = mysql.connector.connect(user=user, database=database, host=host)
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT * FROM tags WHERE "
    whereClause = " OR ".join(["Tag='%s'" % tag for tag in tags])
    query += whereClause

    cursor.execute(query)
    return cursor.fetchall()

  except mysql.connector.Error as err:
    handleConnectionError(err)
  else:
    cnx.close()


def handleConnectionError(err):

  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exists")
  else:
    print(err)

