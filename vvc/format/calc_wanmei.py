#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
from pydota_common import LoadLiveMeizi

Meizi_info = {}


def calc_wanmei(line):
    record = line.strip().split(',')
    if len(record) > 23:
        lid = record[23]
        if lid not in Meizi_info.keys():
            sys.stderr.write(("liderr,%s") % line)
            return
        live_infos = Meizi_info[lid]

        for live_info_one in live_infos:
            activityid = live_info_one[0]
            break

        if str(activityid) == "497":
            print line



if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    start_time = sys.argv[1]
    Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[2:]):
        calc_wanmei(line)
