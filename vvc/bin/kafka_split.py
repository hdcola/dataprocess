#!/usr/bin/env python
# encoding: utf-8
# 从stdin或第四个参数中取得topic指定起止时间的数据，如果时间正常出到stdout，如果不正常出到stderr
#
# python kafka_split.py starttime endtime topic [filepath]
#
# bzcat *.bz2 | python kafka_split.py 201510091000 201510091100 mpp_vv_pcweb
#

import fileinput
import sys
import time
import string
import json
import os

filesfps = []
filesfpscount = 0

def setSplitDone(start_time, dirpath, topic):
    try:
        timedata = time.localtime(start_time)
    except ValueError:
        raise ValueError("timeerr")
    timetmp_date = time.strftime('%Y%m%d%H', timedata)
    f = open(dirpath+"/"+"done_"+str(timetmp_date)+"00_"+topic, 'a+')
    f.close()

def setSplitStart(start_time, dirpath, topic):
    try:
        timedata = time.localtime(start_time)
    except ValueError:
        raise ValueError("timeerr")
    timetmp_date = time.strftime('%Y%m%d%H', timedata)
    try:
        os.remove(dirpath+"/"+"done_"+str(timetmp_date)+"00_"+topic)
    except OSError:
        pass

def testTime(timetmp, start_time, end_time, topic, dirpath):
    if topic == "mpp_vv_pcweb" or topic == "mpp_vv_pcclient" or topic == "mpp_vv_msite":
        try:
            timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
            timeStamp = int(time.mktime(timedata))
        except ValueError:
            raise ValueError("timeerr")
    elif topic == "mpp_vv_mobile" or topic == "mpp_vv_ott" or topic == "ott_vv_41":
        timeStamp = int(timetmp)
    elif topic == "mpp_vv_mobile_new_version" or topic == "mpp_vv_padweb" or topic == "ott_vv_44" \
        or topic == "ott_vv_311_20151012" or topic == "mpp_vv_mobile_211_20151012":
        try:
            timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
            timeStamp = int(time.mktime(timedata))
        except ValueError:
            raise ValueError("timeerr")

    timeexit = int(end_time) + 1800
    if (timeStamp >= int(start_time) and timeStamp <= int(end_time)):
        return True
    elif (timeStamp > timeexit):
        setSplitDone(start_time, dirpath, topic)
        exit(0)
    else:
        return False

def split_kafka(line, start_time, end_time, topic, dirpath):
    if topic == "mpp_vv_pcweb" or topic == "mpp_vv_pcclient" or topic == "mpp_vv_msite":
        record = string.split(line, '- -')
        try:
            record = record[1].strip().split(' ')
        except IndexError:
            sys.stderr.write(("indexerr,%s") % line)
            return
        timetmp = str(record[0]) + str(record[1])
    elif topic == "mpp_vv_mobile" or topic == "mpp_vv_ott" or topic == "ott_vv_41":
        try:
            record = json.loads(line)
        except ValueError:
            sys.stderr.write(("jsonerr,%s") % line)
            return
        timetmp = str(record["time"])
    elif topic == "mpp_vv_mobile_new_version" or topic == "mpp_vv_padweb" or topic == "ott_vv_44" \
          or topic == "ott_vv_311_20151012" or topic == "mpp_vv_mobile_211_20151012":
        record = string.split(line, '\t')
        timetmp = record[0].strip()

    try:
        if testTime(timetmp, start_time, end_time, topic, dirpath):
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

    try:
        topic = sys.argv[3]
    except IndexError:
        topic = "mpp_vv_pcweb"
    dirpath = sys.argv[4]
    setSplitStart(start_time, dirpath, topic)
    for line in fileinput.input(sys.argv[5:]):
        split_kafka(line, start_time, end_time, topic, dirpath)
