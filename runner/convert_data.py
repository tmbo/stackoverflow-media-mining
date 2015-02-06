import ConfigParser
import os
from multiprocessing import Pool
from data_converter.xml2sql import xml2sql

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
    input_file = "%s/%s" % (SO_DATA, cfg.get(so_input, "input"))
    output_file = "%s/%s-%s.sql" % (OUT_DIR, idx+1, so_input)
    converter = xml2sql(input_file, output_file)
    converter.convert(
        tag="row",
        table=cfg.get(so_input, "table"),
        input_fields=cfg.get(so_input, "columns").split(" "))


if __name__ == '__main__':
    ensure_folder_exists(OUT_DIR)
    cfg = from_config()
    pool = Pool()
    pool.map(convert_file, enumerate(cfg.sections()))
    pool.terminate()