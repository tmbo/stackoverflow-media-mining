import os
import ConfigParser


class Database(object):
    def __init__(self, config):
        self.user = config.get("DB", "user")
        self.password = config.get("DB", "password")
        self.password = config.get("DB", "password")
        self.host = config.get("DB", "host")
        self.database = config.get("DB", "database")
        self.db_type = config.get("DB", "typ")


    @staticmethod
    def from_config(file_name='../application.cfg'):
        config = ConfigParser.RawConfigParser()
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        configDir = os.path.join(scriptDir, file_name)
        config.read(configDir)
        return Database(config)

    def connection(self):
        if self.db_type == "mysql":
            import mysql.connector
            return mysql.connector.connect(user=self.user,
                                           database=self.database,
                                           host=self.host)
        elif self.db_type == "hana":
            import dbapi
            return dbapi.connect(address=self.host,
                                 port=self.port,
                                 user=self.user,
                                 password=self.password)
        else:
            raise Exception("Unknown database type setting in application configuration.")

    def cursor(self, **kwargs):
        con = self.connection()
        return con, con.cursor(**kwargs)

    def paged_query(self, select, from_, where, start_offset=0, page_size=50000, subsample=1.0):
        # We need to use pagination here. Since we are expecting something around 8 million results the cursor will time
        # out before we get a chance to process all posts
        # print "called page query"

        last_id = start_offset
        is_empty = False
        _where = "WHERE " + where if where is not None else ""
        _select = ", " + select if select is not None else ""
        query_template = "SELECT Id %s FROM %s %s AND Id > %d ORDER BY Id ASC LIMIT %d"
        try:
            db = self.connection()

            con, cursor = db.cursor()
            while not is_empty:
                # print "Running query: %s" % query_template % (_select, from_, _where, last_id, page_size)
                cursor.execute(query_template % (_select, from_, _where, last_id, page_size))
                results = cursor.fetchall()
                # print "Fetched results."

                if len(results) > 0:
                    last_id = results[-1][0]
                    if subsample != 1.0:
                        end_idx = min(int(page_size * subsample), len(results))
                        yield results[0:end_idx]
                    else:
                        yield results
                else:
                    is_empty = True

        except Exception as err:
            print "Database ERROR: "
            print err
            db.close()
            print "Rec call: "
            for r in self.paged_query(select, from_, where, last_id, page_size, subsample=subsample):
                yield r
        else:
            db.close()
