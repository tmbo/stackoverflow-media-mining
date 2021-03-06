"""
  Modified version of xml2csv.py from
  Kailash Nadh, http://nadh.in
  October 2011
  
  License:        MIT License
  Documentation:    http://nadh.in/code/xmlutils.py
"""

import codecs
import xml.etree.ElementTree as et
from dateutil.parser import parse


class xml2sql:
    
    def __init__(self, input_file):
        """Initialize the class with the paths to the input xml file
        and the output sql file
        Keyword arguments:
        input_file -- input xml filename
        output_file -- output sql filename
        encoding -- character encoding
        """

        self.output_buffer = []
        self.output = None
        self.num_insert = 0

        # open the xml file for iteration
        self.context = et.iterparse(input_file, events=("start", "end"))

    def _escape_csv_value(self, v, is_timestamp):
        if is_timestamp:
            try:
                time = parse(v)
                return time.strftime("%Y-%m-%d %H:%M:%S.%f0")
            except ValueError:
                return None
        else:
            return v.replace('\n', r'\n').replace("'", r"''")
    
    def _as_csv(self, value, is_timestamp):
        if value is None:
            return None
        else:
            return self._escape_csv_value(value, is_timestamp)

    def convert(self, tag="item", input_fields=None, timestamps=set(), limit=-1, packet=8):
        """Convert the XML file to SQL file
             Keyword arguments:
            tag -- the record tag. eg: item
            table -- table name
            ignore -- list of tags to ignore
            limit -- maximum number of records to process
            packet -- maximum size of an insert query in MB (MySQL's max_allowed_packet)
            Returns:
            {	num: number of records converted,
                num_insert: number of sql insert statements generated
            }
        """

        self.context = iter(self.context)

        # get to the root
        event, root = self.context.next()

        fields = input_fields

        sql_len = 0
        n = 0

        max_packet = 5000


        # iterate through the xml
        for event, elem in self.context:
            # if elem is an unignored child node of the record tag, it should be written to buffer
            # should_write = elem.tag not in ignore
            if event == "end" and elem.tag == tag:
                row = map(lambda fname: self._as_csv(elem.attrib.get(fname, None), fname in timestamps), fields)

                sql_len += len(row)

                if sql_len < max_packet:
                    # store the sql statement in the buffer
                    self.output_buffer.append(tuple(row))
                else:
                    # packet size exceeded. flush the sql and start a new insert query
                    yield self.output_buffer
                    self.output_buffer = []
                    self.num_insert += 1
                    
                    self.output_buffer.append(tuple(row))
                    sql_len = 0

                n += 1

                # halt if the specified limit has been hit
                if n == limit:
                    break

                # It's safe to call clear() here because no descendants will be
                # accessed
                elem.clear()
                root.clear()
