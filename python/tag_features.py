import mysql.connector
from mysql.connector import errorcode
import itertools

def log(stats):

  print "PostID: ", stats["postId"]
  print "Average frequency of Tags : ", stats["tag_popularity"]
  print "Number of Popular Tags (25): ", stats["num_pop_tags_25"]
  print "Number of Popular Tags (50): ", stats["num_pop_tags_50"]
  print "Number of Popular Tags (100): ", stats["num_pop_tags_100"]
  print "Average co-occurance of Tags: ", stats["tag_specificity"]
  print "-----------------------------------------"


def numberOfPopularTags(tagStats, threshold):
  print tagStats
  return reduce(lambda sum, x: sum + (1 if x["Count"] > threshold else 0),tagStats , 0)


def tagPopularity(tagStats):
  return reduce(lambda sum, x: sum + x["Freq"] ,tagStats , 0) / len(tagStats)


def tagSpecificity(tags):
  #itertools.combination()
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

  print log(stats)
  return stats


# ========= Main Entry Point ============
def queryTagStatistic(tags):

  try:

    cnx = mysql.connector.connect(user="root",
                                  database="stackoverflow",
                                  host="localhost")

    cursor = cnx.cursor(dictionary=True)
    query = "SELECT * FROM tags WHERE "
    whereClause = " OR ".join(["Tag='%s'" % tag for tag in tags])
    query += whereClause
    print query
    cursor.execute(query)

    # HACKY
    return cursor.fetchall()


  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exists")
    else:
      print(err)
  else:
    cnx.close()

