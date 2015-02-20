import csv
import codecs


def read_csv(filename, included_column_names, subsample=1.0, limit=None):
    with open(filename, "rb") as csv_file:
        try:
            data_reader = csv.reader(csv_file)
            idx = 0
            count = 0
            yield_count = 0
            take_max = subsample * 1000
            included_columns = []
            for row in data_reader:
                if idx == 0:
                    included_columns = [i for i, column in enumerate(row) if column in included_column_names]
                elif count < take_max:
                    yield_count += 1
                    yield [row[i].decode('unicode_escape').encode('ascii','ignore') for i in included_columns]
                idx += 1
                if idx % 1000 == 0:
                    count = 0
                else:
                    count += 1
                if limit is not None and yield_count >= limit:
                    return
        except Exception as err:
            print "Caught an error while reading csv line %d" % idx
            print err
            return