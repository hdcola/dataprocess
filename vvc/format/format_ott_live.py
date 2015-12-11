#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
from pydota_common import write_to_file
import json


def collectFiled(formatlist, record, index, filed, islower=True, isnull=True):
    if filed in record.keys():
        if not isnull:
            if str(record[filed]) == "":
                write_to_file(("%s_err,%s") % (filed, line), topic, log_time, start_time, "des_err")
                raise ValueError("args is null")
                return

        if islower:
            formatlist[index] = str(record[filed]).lower()
        else:
            formatlist[index] = str(record[filed])
    else:
        write_to_file(("%s_err,%s") % (filed, line), topic, log_time, start_time, "des_err")
        raise ValueError("args is illegal")
        return


def ott_live_format(line):
    global log_time
    formatlist = [""]*27
    if len(line.strip('\n')) == 0:
        return
    if "play_realtime" not in line:
        write_to_file("playrealtimeerr,%s" % line, topic, start_time, start_time, "orig_err")
        return

    try:
        record_tmp = json.loads(line)
        if "play_realtime" in record_tmp.keys():
            record = record_tmp["play_realtime"]
        else:
            write_to_file("playrealtimeerr,%s" % line, topic, start_time, start_time, "orig_err")
            return
    except ValueError:
        write_to_file("jsonerr,%s" % line, topic, start_time, start_time, "orig_err")
        return

    if "date" in record.keys():
        date_tmp = record["date"]
        formatlist[0] = str(date_tmp)
    else:
        write_to_file("date_err,%s" % line, topic, start_time, start_time, "orig_err")
        return

    if "index_record" in record.keys():
        time_tmp = record["index_record"]
        formatlist[1] = str(time_tmp)
    else:
        write_to_file("index_record_err,%s" % line, topic, start_time, start_time, "orig_err")
        return

    log_time = date_tmp + time_tmp[:2] + "00"

    # 写入时间正确的原始到orig文件
    write_to_file(line, topic, log_time, start_time, "orig")

    try:
        formatlist[16] = "4"
        formatlist[20] = "play"
        formatlist[21] = "ott"
        formatlist[26] = "-"
        collectFiled(formatlist, record, 15, "user_cookie")
        collectFiled(formatlist, record, 23, "source_id", False, False)
    except ValueError:
        return

    write_to_file(','.join(formatlist), topic, log_time, start_time, "des")


if __name__ == '__main__':
    # loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    # Meizi_info = LoadLiveMeizi(start_time)
    topic = "ott_live"
    for line in fileinput.input(sys.argv[3:]):
        ott_live_format(line)
