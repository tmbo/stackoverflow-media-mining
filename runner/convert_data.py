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


def convert_file(data):
    idx, so_input = data
    print "Converting %s..." % cfg.get(so_input, "input")
    
    input_file = "%s/%s" % (SO_DATA, cfg.get(so_input, "input"))
    output_file = "%s/%s-%s.sql" % (OUT_DIR, idx+1, so_input)
    converter = xml2sql(input_file, output_file)
    converter.convert(
        tag="row",
        table=cfg.get(so_input, "table"),
        input_fields=cfg.get(so_input, "columns").split(" "))


def import_files_into_db():
    database = Database.from_config()
    connection, cursor = database.cursor()
    print "Creating stackoverflow tables..."
    execute_sql_from_file("runner/0-create-so-tables.sql", cursor)
    cursor.close()
    print "Finished creating stackoverflow tables..."

    for sql_file in glob.glob('%s/*.sql' % OUT_DIR):
        print "Running SQL script %s ..." % sql_file
        cursor = connection.cursor()
        execute_sql_from_large_file(sql_file, cursor)
        cursor.close()
    connection.close()
    

if __name__ == '__main__':
    ensure_folder_exists(OUT_DIR)
    cfg = from_config()
    pool = Pool()
    pool.map(convert_file, enumerate(cfg.sections()))
    pool.terminate()

    import_files_into_db()
