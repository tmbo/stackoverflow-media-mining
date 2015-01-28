import ConfigParser
import mysql.connector
import itertools
from mysql.connector import errorcode
import re
import time
from database import Database

TAG_EXTRACTOR = re.compile(r'<([^>]+)>')
page_size = 50000
start_time = int(time.time())
tag_counter = {}
tag_ids = {}
tag_combos_counter = {}
num_questions = 0
post_tag_cache = []


def createTagsTable(cursor, writer):
    cursor.execute("""CREATE TABLE `tags` (
      `Id` int(11) NOT NULL AUTO_INCREMENT,
      `Tag` mediumtext,
      `Count` int(11) NOT NULL,
      `Freq` DOUBLE NOT NULL,
      PRIMARY KEY (`Id`)
    )""")
    writer.commit()


def createTagCombosTable(cursor, writer):
    cursor.execute("""CREATE TABLE `tag_combos` (
      `Id` int(11) NOT NULL AUTO_INCREMENT,
      `Tag1` mediumtext,
      `Tag2` mediumtext,
      `Count` int(11) NOT NULL,
      `Togetherness` DOUBLE NOT NULL,
      PRIMARY KEY (`Id`)
    )""")
    writer.commit()


def emptyTagPostTable(cursor, writer):
    cursor.execute("""TRUNCATE TABLE `tag_posts`""")
    writer.commit()

def createTagPostTable(cursor, writer):
    cursor.execute("""CREATE TABLE `tag_posts` (
      `Id` int(11) NOT NULL AUTO_INCREMENT,
      `TagId` int(11),
      `PostId` int(11),
      PRIMARY KEY (`Id`)
    )""")
    writer.commit()


def insertIntoTags(data, cursor, writer):
    try:
        query = """INSERT INTO tags(Id, Tag, Count, Freq) VALUES (%s, %s, %s, %s)"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN insert into TAGS: "
        print err
        raise


def insertIntoTagCombos(data, cursor, writer):
    try:
        query = """INSERT INTO tag_combos(Tag1, Tag2, Count, Togetherness) VALUES (%s, %s, %s, %s)"""
        cursor.executemany(query, data)
        writer.commit()
    except mysql.connector.Error as err:
        print "ERROR IN insert into TAG COMBOS: "
        print err
        raise err


def insertIntoTagPostMap(data, cursor, writer):
    try:
        query = """INSERT INTO tag_posts(TagId, PostId) VALUES (%s, %s)"""
        cursor.executemany(query, data)
        writer.commit()
    except mysql.connector.Error as err:
        print "ERROR IN insert into TAG POST Map: "
        print err
        raise


def write_results_to_db():
    try:
        writer = mysql.connector.connect(user="root",
                                         database="stackoverflow",
                                         host="localhost")

        write_cursor = writer.cursor()
        tag_data = []
        for tag, count in tag_counter.iteritems():
            tag_data.append((tag_ids[tag], tag, count, 1.0 * count / num_questions))
            if len(tag_data) >= 5000:
                insertIntoTags(tag_data, write_cursor, writer)
                tag_data = []

        insertIntoTags(tag_data, write_cursor, writer)
        print "Finished inserting tags"

        tag_tag_data = []
        for tag_combo, count in tag_combos_counter.iteritems():
            togetherness = 1.0 * count * num_questions / (tag_counter[tag_combo[0]] * tag_counter[tag_combo[1]])
            tag_tag_data.append((tag_combo[0], tag_combo[1], count, togetherness))
            if len(tag_tag_data) >= 5000:
                insertIntoTagCombos(tag_tag_data, write_cursor, writer)
                tag_tag_data = []

        insertIntoTagCombos(tag_tag_data, write_cursor, writer)
        writer.close
    except mysql.connector.Error as err:
        print "ERROR IN write results to db: "
        print err


def prepare_db():
    try:
        cnx = mysql.connector.connect(user="root",
                                      database="stackoverflow",
                                      host="localhost")
        cursor = cnx.cursor()
        emptyTagPostTable(cursor, cnx)
    except mysql.connector.Error as err:
        print "ERROR: "
        print err
        cnx.close()
    else:
        cnx.close()


def analyze_posts(start_offset):
    # We need to use pagination here. Since we are expecting something around 8 million results the cursor will time
    # out before we get a chance to process all posts
    global num_questions

    config = ConfigParser.RawConfigParser()
    config.read('application.cfg')
    
    db = Database(config)

    writer, write_cursor = db.cursor()

    for row in db.paged_query(select="Tags", from_="posts", where="ParentId is null", include_id=True):
        tag_string = row[1]
        if tag_string is not None:
            tags = TAG_EXTRACTOR.findall(tag_string)

            for tag in tags:
                tag_counter[tag] = 1 + tag_counter.get(tag, 0)
                if tag in tag_ids:
                    tag_id = tag_ids[tag]
                else:
                    tag_id = len(tag_ids) + 1
                    tag_ids[tag] = tag_id
                post_tag_cache.append((tag_id, row[0]))

            for tag_combo in itertools.combinations(sorted(tags), 2):
                tag_combos_counter[tag_combo] = 1 + tag_combos_counter.get(tag_combo, 0)

            if num_questions % 2000 == 0:
                insertIntoTagPostMap(post_tag_cache, write_cursor, writer)
                del post_tag_cache[:]
                print "%d. %d s %s" % (num_questions, (int(time.time()) - start_time), tags)

        num_questions += 1
    insertIntoTagPostMap(post_tag_cache, write_cursor, writer)

# ========= Main Entry Point ============
if __name__ == "__main__":
    prepare_db()
    print "Starting TAG number crunching\n"
    analyze_posts(0)
    print "Done"
    write_results_to_db()

    print "Finished inserting tag combinations"

