#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string

filesfps = []
filesfpscount = 0
def testTime(timetmp, start_time, end_time):
    try:
        timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
        timeStamp = int(time.mktime(timedata))
    except ValueError:
        raise ValueError("timeerr")
    timeexit = int(end_time) + 600
    if (timeStamp >= int(start_time) and timeStamp <= int(end_time)):
        return True
    elif (timeStamp > timeexit):
        exit(0)
    else:
        return False

def split_kafka(line, start_time, end_time):
    record = string.split(line, '- -')
    try:
        record = record[1].strip().split(' ')
    except IndexError:
        sys.stderr.write(("indexerr,%s") % line)
        return

    timetmp = str(record[0]) + str(record[1])
    try:
        if testTime(timetmp, start_time, end_time):
            print line.strip('\n')
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)


if __name__ == '__main__':
    # gzcat abc.gz | python split_kafka.py start_time end_time  -
    # python split_kafka.py start_time end_time afile bfile cfile
    start_time = sys.argv[1]
    if len(start_time) != 12:
        start_time = str(start_time) + "0"*(12-len(start_time))
    timedata = time.strptime(start_time, "%Y%m%d%H%M")
    start_time = int(time.mktime(timedata))

    end_time = sys.argv[2]
    if len(end_time) != 12:
        end_time = str(end_time) + "0"*(12-len(end_time))
    timedata = time.strptime(end_time, "%Y%m%d%H%M")
    end_time = int(time.mktime(timedata))

    for line in fileinput.input(sys.argv[3:]):
        split_kafka(line, start_time, end_time)
