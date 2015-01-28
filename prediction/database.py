import mysql.connector
from mysql.connector import errorcode


class Database(object):
    def __init__(self, config):
        self.user = config.get("DB", "user")
        self.password = config.get("DB", "password")
        self.host = config.get("DB", "host")
        self.database = config.get("DB", "database")

    def connection(self):
        return mysql.connector.connect(user=self.user,
                                       database=self.database,
                                       host=self.host)

    def cursor(self, **kwargs):
        con = self.connection()
        return con, con.cursor(**kwargs)

    def paged_query(self, select, from_, where, start_offset=0, page_size=50000):
        # We need to use pagination here. Since we are expecting something around 8 million results the cursor will time
        # out before we get a chance to process all posts
        print "called page query"

        last_id = start_offset
        is_empty = False
        _where = "WHERE " + where if where is not None else ""
        _select = ", " + select if select is not None else ""
        query_template = "SELECT Id %s FROM %s %s AND Id > %d ORDER BY Id ASC LIMIT %d"
        try:
            db = self.connection()

            cursor = db.cursor()
            while not is_empty:
                # print "Running query: %s" % query_template % (_select, from_, _where, last_id, page_size)
                cursor.execute(query_template % (_select, from_, _where, last_id, page_size))
                results = cursor.fetchall()
                # print "Fetched results."
                if len(results) > 0:
                    last_id = results[-1][0]
                    yield results
                else:
                    is_empty = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print "ERROR: "
                print err
                db.close()
                print "Rec call: "
                for r in self.paged_query(select, from_, where, last_id, page_size):
                    yield r
        else:
            db.close()
