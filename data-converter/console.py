"""
  Modified version of xml2csv.py from
  Kailash Nadh, http://nadh.in
  October 2011

  License:        MIT License
  Documentation:    http://nadh.in/code/xmlutils.py
"""

import argparse
from xml2sql import xml2sql


def run_xml2sql():
    print """xml2sql by Kailash Nadh (http://nadh.in) --help for help"""

    # parse arguments
    parser = argparse.ArgumentParser(description='Convert an xml file to sql.')
    parser.add_argument('--input', type=file, dest='input_file', required=True, help='input xml filename')
    parser.add_argument('--output', dest='output_file', required=True, help='output sql filename')
    parser.add_argument('--tag', dest='tag', required=True, help='the record tag. eg: item')
    parser.add_argument('--table', dest='table', required=True, help='table name')
    parser.add_argument('--input_fields', dest='input_fields', default=None, nargs='+', help='list of tags to ignore')
    parser.add_argument('--encoding', dest='encoding', default='utf-8', help='character encoding (default=utf-8)')
    parser.add_argument('--limit', type=int, dest='limit', default=-1, help='maximum number of records to process')
    parser.add_argument('--packet', type=float, dest='packet', default='8', \
                        help=r'maximum size of an insert query in MB. \
						see MySQL\'s max_allowed_packet (default=8)')

    args = parser.parse_args()

    converter = xml2sql(args.input_file, args.output_file, args.encoding)
    num = converter.convert(tag=args.tag, table=args.table, input_fields=args.input_fields, limit=args.limit, packet=args.packet)

    print "\n\nWrote", num['num'], "records to", args.output_file, \
        " (INSERT queries =", num['num_insert'], ")"


if __name__ == '__main__':
    run_xml2sql()