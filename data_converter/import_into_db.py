import re


def execute_sql_from_large_file(filename, cursor):
    # Execute every command from the input file
    with open(filename) as sql_file:
        for sql_command in sql_file:
            try:
                c = re.sub(r";$", "", sql_command.strip())
                cursor.execute(c)
            except Exception, msg:
                print "Command skipped: ", msg


def execute_sql_from_file(filename, cursor):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sql_file = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sql_commands = sql_file.split(';')

    # Execute every command from the input file
    for command in sql_commands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            cursor.execute(command)
        except Exception, msg:
            print "Command skipped: ", msg[:75]
