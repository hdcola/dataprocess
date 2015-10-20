#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from getopt import getopt, GetoptError
import bz2
import json
import csv


def genCsvFileName(start_time, key):
    reportdir = "/Users/guodongxu/Work/src/dataprocess/vvc/bin/" + str(start_time)[0:4] + "/" + str(start_time)[4:6]
    # reportdir = "/home/xuguodong/pydota/report/" + str(start_time)[0:4] + "/" + str(start_time)[4:6]
    return str(reportdir)+"/"+str(key)+"_"+str(start_time)+"_vv.csv"


def join_str(str_src, dicta, name):
    if name in dicta:
        str_src = str_src + "," + str(dicta[name])
    else:
        str_src = str_src + ","
    return str_src


def output_version_report(platform_key, report, start_time):
    csvfilename = genCsvFileName(start_time, platform_key)
    cfp = open(csvfilename, 'a+')

    title = platform_key + "版本,总计,综艺,电视剧,电影,音乐,纪录片,原创,动漫,生活,女性,新闻,品牌专区,其他\n"
    cfp.write(title)
    for key, value in report.items():
        if str(key) != "total":
            str_tmp = str(key) + "," + str(value["total"])
            for i in range(1, 10):
                str_tmp = join_str(str_tmp, value, str(i))
            str_tmp = join_str(str_tmp, value, "119")
            str_tmp = join_str(str_tmp, value, "0")

            constr = str_tmp + "\n"
            cfp.write(constr)

    value_total = report["total"]
    str_tmp = "total," + str(value_total["total"])
    for i in range(1, 10):
        str_tmp = join_str(str_tmp, value_total, str(i))
    str_tmp = join_str(str_tmp, value_total, "119")
    str_tmp = join_str(str_tmp, value_total, "0")

    str_total = str_tmp + '\n'
    cfp.write(str_total)
    cfp.close()


def output_total_report(report, start_time):
    csvfilename = genCsvFileName(start_time, "total")
    cfp = open(csvfilename, 'a+')
    title = "平台,总计,综艺,电视剧,电影,音乐,纪录片,原创,动漫,生活,女性,新闻,品牌专区,其他\n"
    cfp.write(title)
    for key, value in report.items():
        if str(key) != "total":
            str_tmp = str(key) + "," + str(value["total"])
            for i in range(1, 10):
                str_tmp = join_str(str_tmp, value, str(i))
            str_tmp = join_str(str_tmp, value, "119")
            str_tmp = join_str(str_tmp, value, "0")

            constr = str_tmp + "\n"
            cfp.write(constr)

    value_total = report["total"]
    str_tmp = "total," + str(value_total["total"])
    for i in range(1, 10):
        str_tmp = join_str(str_tmp, value_total, str(i))
    str_tmp = join_str(str_tmp, value_total, "119")
    str_tmp = join_str(str_tmp, value_total, "0")

    str_total = str_tmp + '\n'
    cfp.write(str_total)
    cfp.close()



def process(start_time, args):
    wrong_num = 0
    version_report = {"ott": {"total": {"total": 0}},
                      "pcweb": {"total": {"total": 0}},
                      "android": {"total": {"total": 0}},
                      "iphone": {"total": {"total": 0}},
                      "ipad": {"total": {"total": 0}},
                      "apad": {"total": {"total": 0}},
                      "phonem": {"total": {"total": 0}},
                      "padweb": {"total": {"total": 0}},
                      "pcclient": {"total": {"total": 0}}
    }

    channel = {"1": "综艺",
               "2": "电视剧",
               "3": "电影",
               "4": "音乐",
               "5": "纪录片",
               "6": "原创",
               "7": "动漫",
               "8": "生活",
               "9": "女性",
               "10": "新闻",
               "119": "品牌专区"}

    total_report = {"total": {"total": 0}}
    for arg in args:
        arg = os.path.abspath(arg)
        base = os.path.basename(arg)
        filename, ext = os.path.splitext(base)
        if os.path.isfile(arg):
            if ext == ".bz2":
                fp = bz2.BZ2File(arg)
            else:
                fp = open(arg)

        for i, line in enumerate(fp):
            try:
                record = line.split(',')
                platform = record[21].strip()
                version = record[22].strip()
                cid = str(record[10].strip())
                channel_name = "0"
                if cid in channel:
                    channel_name = str(cid)

                # 计算各个平台各个版本的总vv。以及各频道总vv
                # 从三个纬度计算，先算version,再算频道，再汇总

                # 从version角度计算
                if platform not in version_report:
                    wrong_num += 1
                    continue
                try:
                    version_report[platform][version]["total"] += 1
                    version_report[platform]["total"]["total"] += 1
                except KeyError:
                    version_report[platform][version] = {}
                    version_report[platform][version]["total"] = 1
                    version_report[platform]["total"]["total"] += 1

                # 从频道纬度计算,计算各个版本的的vv
                try:
                    if platform != "ott":
                        version_report[platform][version][channel_name] += 1
                except KeyError:
                    if platform != "ott":
                        version_report[platform][version][channel_name] = 1

                # 计算各个平台的某一频道的总vv.
                try:
                    if platform != "ott":
                        version_report[platform]["total"][channel_name] += 1
                except KeyError:
                    if platform != "ott":
                        version_report[platform]["total"][channel_name] = 1

                # 计算总表中,总vv以及各个平台总vv
                try:
                    total_report[platform]["total"] += 1
                    total_report["total"]["total"] += 1
                except KeyError:
                    total_report["total"]["total"] += 1
                    total_report[platform] = {}
                    total_report[platform]["total"] = 1

                # 计算各平台下各个频道的vv
                try:
                    if platform != "ott":
                        total_report[platform][channel_name] += 1
                except KeyError:
                    if platform != "ott":
                        total_report[platform][channel_name] = 1

                # 计算全平台的各个频道的总vv
                try:
                    if platform != "ott":
                        total_report["total"][channel_name] += 1
                except KeyError:
                    if platform != "ott":
                        total_report["total"][channel_name] = 1

            except IndexError:
                print "IndexError"

    output_total_report(total_report, start_time)
    for platform_key in version_report.keys():
        output_version_report(platform_key, version_report[platform_key], start_time)

    # print json.dumps(total_report, ensure_ascii=False)
    # print "==========="
    sys.stderr.write(("数据格式错误数目: %s\n") % str(wrong_num))
    # print "==========="
    # for key, value in version_report.items():
    #     # result = sorted(value.iteritems(), key=lambda ab: ab[1], reverse=True)
    #     print key + ":" + str(value)
    # print version_report


def main():
    try:
        opts, args = getopt(sys.argv[1:], 't:')
    except GetoptError:
        sys.stderr.write("get opts erron\n")
        sys.exit(-1)

    start_time = ""
    for opt in opts:
        if opt[0] == "-t":
            start_time = opt[1]
        else:
            sys.exit(-1)

    process(start_time, args)


if __name__ == "__main__":
    main()

