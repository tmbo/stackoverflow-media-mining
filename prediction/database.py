import os
import ConfigParser


# DB API endpoint. Uses a configuration file to connect to a DB
# Provides convenience wrappers to access cursor methods and 
# for paginated queries
class Database(object):
    def __init__(self, config):
        self.user = config.get("DB", "user")
        self.password = config.get("DB", "password")
        self.port = config.get("DB", "port")
        self.host = config.get("DB", "host")
        self.database = config.get("DB", "database")
        self.db_type = config.get("DB", "typ")


    # Load the database settings from file
    @staticmethod
    def from_config(file_name='../application.cfg'):
        config = ConfigParser.RawConfigParser()
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        configDir = os.path.join(scriptDir, file_name)
        config.read(configDir)
        return Database(config)

    # Create a new connection using the specified settings
    def connection(self):
        if self.db_type == "mysql":
            import mysql.connector
            return mysql.connector.connect(user=self.user,
                                           database=self.database,
                                           host=self.host)
        elif self.db_type == "hana":
            import dbapi
            return dbapi.connect(address=self.host,
                                 port=int(self.port),
                                 user=self.user,
                                 password=self.password)
        else:
            raise Exception("Unknown database type setting in application configuration.")

    # Create a cursor for DB queries
    def cursor(self, **kwargs):
        con = self.connection()
        return con, con.cursor(**kwargs)

    # Execute a paged query. Mostly necessary for slow DBs like mysql. Otherwise the DB
    # will not respond if the query result is to big.
    def paged_query(self, select, from_, where, start_offset=0, page_size=50000, subsample=1.0, id_prefix=None):
        _prefix = id_prefix + "." if id_prefix is not None else ""
        last_id = start_offset
        is_empty = False
        _where = "WHERE " + where if where is not None else ""
        _select = ", " + select if select is not None else ""
        query_template = "SELECT %sId %s FROM %s %s AND %sId > %d ORDER BY %sId ASC LIMIT %d"
        try:
            con, cur = self.cursor()
            # We are going to sort by id and query one page after another. If the 
            # query fails we are going to repeat it. This might lead to SO if a 
            # query always fails.
            while not is_empty:
                # print "Running query: %s" % query_template % (_prefix, _select, from_, _where, _prefix, last_id, _prefix, page_size)
                cur.execute(query_template % (_prefix, _select, from_, _where, _prefix, last_id, _prefix, page_size))
                results = cur.fetchall()
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
            con.close()
            print "Rec call: "
            for r in self.paged_query(select, from_, where, last_id, page_size, subsample=subsample, id_prefix=id_prefix):
                yield r
        else:
            con.close()
