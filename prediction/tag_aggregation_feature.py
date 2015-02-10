import itertools
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


def create_tags_table(cursor, writer):
    try:
        cursor.execute("""CREATE TABLE SO_TAGS (
          Id    INT    NOT NULL PRIMARY KEY,
          Tag   VARCHAR(255),
          Count INT    NOT NULL,
          Freq  DOUBLE NOT NULL
        )""")
    except Exception:
        return


def create_tag_combos_table(cursor, writer):
    try:
        cursor.execute("""CREATE TABLE SO_TAG_COMBOS (
          Id           INT    NOT NULL PRIMARY KEY,
          Tag1         VARCHAR(255),
          Tag2         VARCHAR(255),
          Count        INT    NOT NULL,
          Togetherness DOUBLE NOT NULL
        )""")
    except Exception:
        return


def empty_tag_post_table(cursor, writer):
    try:
        cursor.execute("""TRUNCATE TABLE SO_TAG_POSTS""")
    except Exception:
        return


def create_tag_post_table(cursor, writer):
    try:
        cursor.execute("""CREATE TABLE SO_TAG_POSTS (
          Id int NOT NULL PRIMARY KEY,
          TagId int,
          PostId int
        )""")
    except Exception:
        return


def insert_into_tags(data, cursor, writer):
    try:
        query = """INSERT INTO SO_TAGS(Id, Tag, Count, Freq) VALUES (?,?,?,?)"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN insert into TAGS: "
        print err
        raise


def insert_into_tag_combos(data, cursor, writer):
    try:
        query = """INSERT INTO SO_TAG_COMBOS(Id, Tag1, Tag2, Count, Togetherness) VALUES (?,?,?,?,?)"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN insert into TAG COMBOS: "
        print err
        raise err


def insert_into_tag_post_map(data, cursor, writer):
    try:
        query = """INSERT INTO SO_TAG_POSTS(Id, TagId, PostId) VALUES (?, ?, ?)"""
        cursor.executemany(query, data)
        writer.commit()
    except Exception as err:
        print "ERROR IN insert into TAG POST Map: "
        print err
        raise


def write_results_to_db():
    try:
        database = Database.from_config()

        writer, write_cursor = database.cursor()
        tag_data = []
        idx = 1
        for tag, count in tag_counter.iteritems():
            tag_data.append((tag_ids[tag], tag, count, 1.0 * count / num_questions))
            idx += 1
            if len(tag_data) >= 5000:
                insert_into_tags(tag_data, write_cursor, writer)
                tag_data = []

        insert_into_tags(tag_data, write_cursor, writer)
        print "Finished inserting tags"

        tag_tag_data = []
        idx = 1
        for tag_combo, count in tag_combos_counter.iteritems():
            togetherness = 1.0 * count * num_questions / (tag_counter[tag_combo[0]] * tag_counter[tag_combo[1]])
            tag_tag_data.append((idx, tag_combo[0], tag_combo[1], count, togetherness))
            idx += 1
            if len(tag_tag_data) >= 5000:
                insert_into_tag_combos(tag_tag_data, write_cursor, writer)
                tag_tag_data = []

        insert_into_tag_combos(tag_tag_data, write_cursor, writer)
        writer.close()
    except Exception as err:
        print "ERROR IN write results to db: "
        print err


def prepare_db():
    connection = None
    try:
        cnx = Database.from_config()
        connection, cursor = cnx.cursor()
        create_tags_table(cursor, cnx)
        create_tag_combos_table(cursor, cnx)
        create_tag_post_table(cursor, cnx)
    except Exception as err:
        print "ERROR: "
        print err
        if connection:
            connection.close()
    else:
        connection.close()


def analyze_posts():
    # We need to use pagination here. Since we are expecting something around 8 million results the cursor will time
    # out before we get a chance to process all posts
    global num_questions

    db = Database.from_config()

    writer, write_cursor = db.cursor()
    
    post_tag_cache_id = 1

    for rows in db.paged_query(select="Tags", from_="SO_POSTS", where="ParentId is null"):
        for row in rows:
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
                    post_tag_cache.append((post_tag_cache_id, tag_id, row[0]))
                    post_tag_cache_id += 1

                for tag_combo in itertools.combinations(sorted(tags), 2):
                    tag_combos_counter[tag_combo] = 1 + tag_combos_counter.get(tag_combo, 0)

                if num_questions % 2000 == 0:
                    insert_into_tag_post_map(post_tag_cache, write_cursor, writer)
                    del post_tag_cache[:]
                    print "%d. %d s %s" % (num_questions, (int(time.time()) - start_time), tags)

            num_questions += 1
    insert_into_tag_post_map(post_tag_cache, write_cursor, writer)

# Analyze all the posts in the DB and calculate the tag statistics and tables
if __name__ == "__main__":
    prepare_db()
    print "Starting TAG number crunching\n"
    analyze_posts()
    print "Done"
    write_results_to_db()

    print "Finished inserting tag combinations"
