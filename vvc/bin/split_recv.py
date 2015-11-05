#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import re
import os

filesfps = []
filesfpscount = 0


def genCsvFileName(org_dirpath, log_time, topic):
    file_str = '{0}/{1}/{2}/{3}_{4}'.format(str(org_dirpath), log_time[0:4], log_time[4:6], log_time, topic)
    file_str = os.path.abspath(file_str)
    dir_name = os.path.dirname(file_str)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return file_str

    # return str(org_dirpath)+"/"+log_time[0:4]+"/"+log_time[4:6]+"/orig_"+log_time+"_"+topic


def output_to_files(log_time, org_dirpath, line, topic):
    str_log_file = genCsvFileName(org_dirpath, log_time, topic)

    if str_log_file in file_list:
        log_file = file_list[str_log_file]
    else:
        try:
            log_file = open(str_log_file, 'a+')
            file_list[str_log_file] = log_file
        except IOError:
            exit(-1)

    log_file.write(line)


def check_time(log_time):
    """
    :summary: 校验log_time是否合理
    :param log_time: 201510101000
    :return: boolean
    """
    if len(log_time) != 12:
        return False
    try:
        return 201000000000 < int(log_time) < 205000000000
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)
        return False



def split_recv(line, topic, org_dirpath):
    """
    :summary: 分topic解析日志，正常日志输出到stdout，异常日志写入stderr
    :param line: recv日志文件获取的一行日志数据
    :param topic: kafka－topic名称
    :param  dirpath orig日志输出基础目录
    :return:
    """
    log_time = ""
    if topic in ["mpp_vv_pcweb", "mpp_vv_pcclient", "mpp_vv_msite"]:
        record = string.split(line, '- -')
        try:
            record = record[1].strip().split(' ')
        except IndexError:
            sys.stderr.write(("indexerr,%s") % line)
            return

        try:
            timetmp = str(record[0]) + str(record[1])
            timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
            log_time = time.strftime("%Y%m%d%H", timedata)
        except (ValueError, KeyError):
            sys.stderr.write(("timeerr,%s") % line)
            return

    elif topic in ["mpp_vv_mobile", "mpp_vv_ott", "ott_vv_41"]:

        regex = ".*\"time\":\"?(\d+)\"?.*"
        pattern = re.compile(regex)
        match = pattern.match(line)
        if not match:
            sys.stderr.write(("timeerr,%s") % line)
            return
        timetmp = match.groups()[0]

        try:
            timedata = time.localtime(int(timetmp))
            log_time = time.strftime("%Y%m%d%H", timedata)
        except ValueError:
            sys.stderr.write(("timeerr, %s") % line)
            return

    elif topic in ["mpp_vv_mobile_new_version", "mpp_vv_padweb", "ott_vv_44",
                   "ott_vv_311_20151012", "mpp_vv_mobile_211_20151012", "rt_live_pcweb", "rt_live_mobile_new"]:
        record = string.split(line, '\t')
        timetmp = record[0].strip()

        try:
            timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
            log_time = time.strftime("%Y%m%d%H", timedata)
        except ValueError:
            sys.stderr.write(("timeerr,%s") % line)
            return

    if check_time(log_time):
        output_to_files(log_time, org_dirpath, line, topic)
    else:
        sys.stderr.write(("timeerr,%s") % line)
        return


if __name__ == '__main__':

    global file_list
    file_list = {}
    topic = ""
    org_dirpath = ""
    try:
        topic = sys.argv[1]
        org_dirpath = sys.argv[2]
    except IndexError:
        print("参数输入错误\n")
        exit(-1)

    for line in fileinput.input(sys.argv[3:]):
        split_recv(line, topic, org_dirpath)

    for key, value in file_list.items():
        value.close()
