#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import urllib
import json
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file, getVersionNum, check_act_field

reload(sys)
sys.setdefaultencoding('utf-8')


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


def mobile_new_version_211_20151012_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    lineall = string.split(line.strip(), '\t')
    try:
        jsonline = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1].strip()
    except IndexError:
        write_to_file(("indexerr,%s") % line, topic, start_time, start_time, "orig_err")
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

    if not check_act_field(jsonline, "aplay"):
        write_to_file("acterr,", topic, log_time, start_time, "des_err")
        return

    try:
        recordall = json.loads(jsonline)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, log_time, start_time, "des_err")
        return
    try:
        record = recordall[0]
    except KeyError:
        record = recordall
    except TypeError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # IP
    try:
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        write_to_file(("iperr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # 提前丢掉act为非play的日志
    try:
        act = record["act"]
        if act.strip() == "":
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        elif act == "aplay":
            act = 'play'
        else:
            return
    except KeyError:
        write_to_file("acterr,", topic, log_time, start_time, "des_err")
        return

    # pt
    try:
        pt = record['pt']
        if str(pt) != '0' and str(pt) != '3' and str(pt) != '4':
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
    except KeyError:
        write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
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

    try:
        # uid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)
        # uuid
        formatstring = collectArgs(formatstring, record, "suuid", "suiderr", False, True)

        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)

        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)
        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        if str(pt) == '0' or str(pt) == '3':
            formatstring = collectArgs(formatstring, record, "cid", "ciderr", False, True)

            #plid
            formatstring = collectArgs(formatstring, record, "plid", "pliderr", False, True)

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
        else:
            formatstring = formatstring + ","
            formatstring = formatstring + ","
            formatstring = formatstring + ","
            formatstring = formatstring + ","
            formatstring = formatstring + ","

        # cookie
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
        formatstring = formatstring + ',' + str(pt)

        # ln
        try:
            ln = record["ln"]
            formatstring = formatstring + ',' + urllib.unquote(str(ln))
        except KeyError:
            formatstring = formatstring + ",-"

        if str(pt) == '0' or str(pt) == '3':
            # cf
            formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        else:
            formatstring = formatstring + ","

        # definition
        formatstring = collectArgs(formatstring, record, "def", "deferr", False, True)

        # act
        formatstring = formatstring + ',' + str(act)

        # CLIENTTP
        try:
            clientver = record["aver"].lower()
            if 'iphone' in clientver:
                clienttp = 'iphone'
            elif 'aphone' in clientver:
                clienttp = 'android'
            elif 'ipad' in clientver:
                clienttp = 'ipad'
            elif 'apad' in clientver:
                clienttp = 'apad'
            else:
                write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(clienttp)
        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # CLIENTVER
        try:
            clientver = record["aver"].lower()
            if "imgotv-aphone" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 453:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            elif "imgotv-iphone" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 455:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            elif "ipad" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 423:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            else:
                write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        if str(pt) == '4':
            # sourceid
            formatstring = collectArgs(formatstring, record, "lid", "liderr", True)
        else:
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
    topic = "mpp_vv_mobile_211_20151012"
    for line in fileinput.input(sys.argv[3:]):
        mobile_new_version_211_20151012_format(line)
