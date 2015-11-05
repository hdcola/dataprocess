#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import json
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file


def collectArgs(fstring, argslist, name, errname, strict):
    try:
        nametmp = argslist[name]
        if strict:
            if str(nametmp).strip() == "":
                write_to_file(("%s,%s") % (errname, line), topic, log_time, start_time, "des_err")
                raise ValueError("args is illegal")
                return
            else:
                fstring = fstring + ',' + str(nametmp)
                return fstring
        else:
            fstring = fstring + ',' + str(nametmp)
            return fstring
    except KeyError:
        write_to_file(("%s,%s") % (errname, line), topic, log_time, start_time, "des_err")
        raise ValueError("args is illegal")
        return


def ott_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = json.loads(line)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # date, time
    try:
        timetmp = float(record['time'])
        timedata = time.localtime(timetmp)
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        log_time = timetmp_date + timetmp_time[:2] + "00"
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError):
        write_to_file(("timeerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # 写入时间正确的原始到orig文件
    write_to_file(line, topic, log_time, start_time, "orig")

    # IP
    try:
        iptmp = record["ip"].strip()
        formatstring = formatstring + ',' + str(iptmp)
    except KeyError:
        write_to_file(("iperr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except (ValueError, TypeError):
        write_to_file(("locationerr,%s") % line, topic, start_time, start_time, "des_err")
        return

    try:
        # uid
        try:
            uid = record["user_id"]
            formatstring = formatstring + ',' + str(uid)
        except KeyError:
            formatstring = formatstring + ',-'
        # uuid
        try:
            uuid = record["play_session"]
            formatstring = formatstring + ',' + str(uuid)
        except KeyError:
            formatstring = formatstring + ',-'
        # guid
        formatstring = formatstring + ','
        # ref
        formatstring = formatstring + ','
        # bid
        formatstring = formatstring + ','
        # cid
        formatstring = formatstring + ','
        # plid
        formatstring = formatstring + ','
        # vid
        try:
            vid_url = record["play_url"]
            index_url = str(vid_url).lower().find("internettv")
            if index_url == -1:
                write_to_file(("viderr,%s") % line, topic, start_time, start_time, "des_err")
                return
            else:
                vid = str(vid_url)[index_url+len("internettv"):]

            if str(vid) == "":
                write_to_file(("viderr,%s") % line, topic, start_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(vid)
        except KeyError:
            write_to_file(("viderr,%s") % line, topic, start_time, start_time, "des_err")
            return
        # tid
        try:
            tid = record["tid"]
            formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ','

        # vts
        formatstring = formatstring + ','
        # cookie
        try:
            mac = record["mac"]
            if str(mac) == "":
                write_to_file(("macerr,%s") % line, topic, start_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(mac).lower()
        except KeyError:
            write_to_file(("macerr,%s") % line, topic, start_time, start_time, "des_err")
            return
        # pt
        formatstring = formatstring + ',' + '0'
        # ln
        formatstring = formatstring + ','
        # cf
        formatstring = formatstring + ','
        # definition
        formatstring = formatstring + ','
        # act
        formatstring = formatstring + ',' + 'play'
        # CLIENTTP
        formatstring = formatstring + ',' + "ott"
        # aver
        try:
            aver = str(record["apk_version"]).lower()
            if str(aver) == "":
                write_to_file(("apk_versionerr,%s") % line, topic, start_time, start_time, "des_err")
                return
            aver_tmp = aver.split('.')
            if aver_tmp[5] == "dxjd" or aver_tmp[5] == "jllt" or aver_tmp[5] == "fjyd" \
                or aver_tmp[5] == "shyd19" or aver_tmp[0] == "yys":
                return
            formatstring = formatstring + ',' + str(aver).lower()
        except KeyError:
            write_to_file(("apk_versionerr,%s") % line, topic, start_time, start_time, "des_err")
            return

        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_ott"
    for line in fileinput.input(sys.argv[3:]):
        ott_format(line)
