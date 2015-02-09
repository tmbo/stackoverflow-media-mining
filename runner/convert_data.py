import ConfigParser
import os
import glob
from multiprocessing import Pool
from data_converter.xml2sql import xml2sql
from prediction.database import Database
from data_converter.import_into_db import execute_sql_from_file, execute_sql_from_large_file

BASE_FOLDER = "output"

SO_DATA = "%s/stackoverflow-data" % BASE_FOLDER

OUT_DIR = "%s/stackoverflow-data-sql" % BASE_FOLDER


def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def from_config(file_name='stackoverflow_data.cfg'):
    config = ConfigParser.RawConfigParser()
    config.read(file_name)
    return config


def import_xml_into_db(data):
    idx, so_input = data
    connection, cursor = database.cursor()
    print "Reading %s..." % cfg.get(so_input, "input")
    
    input_file = "%s/%s" % (SO_DATA, cfg.get(so_input, "input"))
    converter = xml2sql(input_file)
    table = cfg.get(so_input, "table")
    fields = cfg.get(so_input, "columns").split(" ")
    result = converter.convert(
        tag="row",
        table=table,
        input_fields=fields)
    
    for batch in result:    
        sql_insert = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(fields), ', '.join(['?']*len(fields)))
        cursor.executemany(sql_insert, batch)
    
    connection.close()    


def create_db_tables():
    connection, cursor = database.cursor()
    print "Creating stackoverflow tables..."
    execute_sql_from_file("runner/0-create-so-tables.sql", cursor)
    cursor.close()
    connection.close()

if __name__ == '__main__':
    ensure_folder_exists(OUT_DIR)
    cfg = from_config()
    database = Database.from_config()
    create_db_tables()
    pool = Pool()
    pool.map(import_xml_into_db, enumerate(cfg.sections()))
    pool.terminate()
