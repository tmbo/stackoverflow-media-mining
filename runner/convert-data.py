import ConfigParser
from subprocess import call

BASE_FOLDER = "../output"

SO_DATA = "%s/stackoverflow-data" % BASE_FOLDER

OUT_DIR = "%s/stackoverflow-data-sql" % BASE_FOLDER

CONVERTER = "../data-converter/console.py"


def from_config(file_name='../stackoverflow_data.cfg'):
    config = ConfigParser.RawConfigParser()
    return config.read(file_name)


if __name__ == '__main__':
    cfg = from_config()
    for idx, so_input in enumerate(cfg.sections()):
        input_file = "--input %s/%s" % (SO_DATA, cfg.get(so_input, "input"))
        output_file = "--output %s/%s-%s.sql" % (OUT_DIR, idx, so_input)
        table = "--table %s" % cfg.get(so_input, "table")
        columns = "--input_fields %s" % cfg.get(so_input, "columns")
        call(["python ../data-converter/console.py", input_file, output_file, table, columns, "--tag rows"])
