#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import urllib
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file


def collectArgs(fstring, argslist, name, errname, strict, isNaN=False):
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
        if isNaN:
            fstring = fstring + ',-'
            return fstring
        else:
            write_to_file(("%s,%s") % (errname, line), topic, log_time, start_time, "des_err")
            raise ValueError("args is illegal")
            return


def mpp_vv_win10client_511_20151030_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return

    lineall = string.split(line.strip(), '\t')
    try:
        recordtmp = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1].strip()
    except IndexError:
        write_to_file(("indexerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    recordtmp = recordtmp.strip().split('&')

    record = {}
    for recordtmptmp in recordtmp:
        try:
            argkey = recordtmptmp.split('=')[0]
            argvalue = recordtmptmp.split('=')[1]
            record[argkey] = argvalue
        except IndexError:
            write_to_file(("recorderr,%s") % line, topic, start_time, start_time, "orig_err")
            return

    # date, time
    try:
        timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
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
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        write_to_file(("iperr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except (ValueError, TypeError):
        write_to_file(("locationerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # act提前校验
    try:
        act = record["act"]
        if str(act).strip() == "play":
            act = "play"
        elif str(act).strip() == "":
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        else:
            return
    except KeyError:
        write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
        return

    try:
        formatstring = collectArgs(formatstring, record, "uid", "uiderr", False, True)
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)
        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)

        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
         # cid
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False, True)

        # plid
        formatstring = collectArgs(formatstring, record, "plid", "pliderr", False, True)

        # vid
        formatstring = collectArgs(formatstring, record, "vid", "viderr", True)
        # tid
        try:
            tid = record["tid"]
            if tid.strip() == "":
                formatstring = formatstring + ','
            else:
                if tid.find(",") != -1:
                    tid = tid.replace(",", "_")
                formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ',-'
        # vts
        formatstring = collectArgs(formatstring, record, "vts", "vtserr", False, True)

        try:
            cookie = record["did"]
            if str(cookie).strip() == "":
                write_to_file(("diderr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(cookie).lower()
        except KeyError:
            write_to_file(("diderr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # pt
        try:
            pt = record["pt"]
            if str(pt) != '0':
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        formatstring = formatstring + ',' + str(pt)

        formatstring = collectArgs(formatstring, record, "ln", "lnerr", False, True)


        formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        formatstring = collectArgs(formatstring, record, "def", "deferr", False, True)
        # act
        formatstring = formatstring + "," + str(act)

        # CLIENTTP
        formatstring = formatstring + "," + "win10client"

        # aver
        try:
            ver = record["ver"]
            if str(ver) == "":
                write_to_file(("vererr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(ver).lower()
        except KeyError:
            write_to_file(("vererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # sourceid
        formatstring = formatstring + ','

        # cameraid
        formatstring = formatstring + ','
        # activityid
        formatstring = formatstring + ','

        # url
        try:
            url_str = record['url']
            if url_str.strip() == "":
                formatstring = formatstring + ','
            else:
                url_str = urllib.unquote(url_str)
                if url_str.find(",") != -1:
                    url_str = url_str.replace(",", "")
                formatstring = formatstring + ',' + str(url_str)
        except KeyError:
            formatstring = formatstring + ',-'

        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_win10client_511_20151030"
    for line in fileinput.input(sys.argv[3:]):
        mpp_vv_win10client_511_20151030_format(line)
