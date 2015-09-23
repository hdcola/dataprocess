#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import gzip


def formatTime(timetmp):
    timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
    tm_min = timedata.tm_min / 5 * 5 + 5
    tm_hour = timedata.tm_hour
    if tm_min == 60:
        tm_min = '00'
        tm_hour = timedata.tm_hour + 1
    if tm_min < 10:
        tm_min = '0'+str(tm_min)
    if tm_hour < 10:
        tm_hour = '0'+str(tm_hour)
    timetmp = time.strftime('%Y%m%d', timedata)+str(tm_hour)+str(tm_min)
    return timetmp

def split_kafka(line, pipe_type):
    record = string.split(line, ' ')
    timetmp = str(record[3]) + str(record[4])
    timetmp = formatTime(timetmp)
    filename = str(pipe_type) + "_" + str(timetmp)
    fp = open(filename, "a")
    fp.write(line)
    fp.close()


if __name__ == '__main__':
    # gzcat abc.gz | python split_kafka.py "mpp_vv_pcweb" -
    # python split_kafka.py "mpp_vv_pcweb" afile bfile cfile
    try:
        pipe_type = sys.argv[1]
        for line in fileinput.input(sys.argv[2:]):
            split_kafka(line, pipe_type)
    except IndexError as e:
        pipe_type = "mpp_vv_pcweb"
        for line in fileinput.input(sys.argv[1:]):
            split_kafka(line, pipe_type)
