#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import json

filesfps = []
filesfpscount = 0


def testTime(timetmp, start_time, end_time, topic):
    '''
    :param timetmp: 日志时间
    :param start_time: 日志要求的起始时间，时间戳
    :param end_time: 日志要求的结束时间，时间戳
    :param topic: kafka_topic名称
    :return: bool
    '''

    timeStamp = 0
    # 将timetmp转换为int型时间戳格式
    if topic == "mpp_vv_pcweb" or topic == "mpp_vv_pcclient" or topic == "mpp_vv_msite":
        try:
            timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
            timeStamp = int(time.mktime(timedata))
        except ValueError:
            raise ValueError("timeerr")
    elif topic == "mpp_vv_mobile" or topic == "mpp_vv_ott" or topic == "ott_vv_41":
        timeStamp = int(timetmp)
    elif topic == "mpp_vv_mobile_new_version" or topic == "mpp_vv_padweb" or topic == "ott_vv_44":
        try:
            timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
            timeStamp = int(time.mktime(timedata))
        except ValueError:
            raise ValueError("timeerr")

    # 进程退出时间
    time_exit = int(end_time) + 1800

    if (timeStamp >= int(start_time) and timeStamp <= int(end_time)):
        return True
    elif (timeStamp > time_exit):
        exit(0)
    else:
        return False


def split_kafka(line, start_time, end_time, topic):
    '''
    :summary: 分topic解析日志，正常日志输出到stdout，异常日志写入stderr
    :param line: kafka获取的一行日志数据
    :param start_time: 处理日志的起始时间戳
    :param end_time: 处理日志的结束时间戳
    :param topic: kafka－topic名称
    :return:
    '''
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
    elif topic == "mpp_vv_mobile_new_version" or topic == "mpp_vv_padweb" or topic == "ott_vv_44":
        record = string.split(line, '\t')
        timetmp = record[0].strip()

    try:
        if testTime(timetmp, start_time, end_time, topic):
            print line.strip('\n')
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)


if __name__ == '__main__':
    # gzcat abc.gz | python split_kafka.py start_time end_time  -
    # python split_kafka.py start_time end_time afile bfile cfile

    # 将输入的起止时间转换为时间戳
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

    # 逐行解析日志
    for line in fileinput.input(sys.argv[4:]):
        split_kafka(line, start_time, end_time, topic)
