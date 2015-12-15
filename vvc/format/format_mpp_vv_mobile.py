#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import urllib
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file, getVersionNum
import json

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


def mobile_format(line):
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
        timetmp = record['time']
        timedata = time.localtime(timetmp)
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        log_time = timetmp_date + timetmp_time[:2] + "00"
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError, TypeError):
        write_to_file(("timeerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # 写入时间正确的原始到orig文件
    write_to_file(line, topic, log_time, start_time, "orig")

    # IP
    try:
        iptmp = record["ip"].strip()
        formatstring = formatstring + ',' + str(iptmp)
    except KeyError:
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

    try:
        clientver = record["apk_version"].lower()
        if clientver == "4.5.2":
        # 4.5.2属于新版，在旧版中丢掉
            write_to_file(("clientvererr,%s") % line, topic, log_time, start_time, "des_err")
            return
    except KeyError:
        write_to_file(("clientvererr,%s") % line, topic, log_time, start_time, "des_err")
        return

    try:
        # uid
        formatstring = collectArgs(formatstring, record, "user_id", "uiderr", False, True)

        # uuid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)

        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)

        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)
        # bid
        formatstring = collectArgs(formatstring, record, "bid", "biderr", False, True)
        # cid
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False, True)

        # plid
        formatstring = collectArgs(formatstring, record, "plid", "pliderr", False, True)

        # vid
        try:
            vid = record["video_info"]["video_id"]
            if str(vid).strip() == "":
                write_to_file(("viderr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(vid)
        except KeyError:
            write_to_file(("viderr,%s") % line, topic, log_time, start_time, "des_err")
            return

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
        # cookie
        try:
            cookie = record["mac"]
            if str(cookie).strip() == "":
                write_to_file(("macerr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(cookie).lower()
        except KeyError:
            write_to_file(("macerr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # pt
        try:
            data_type = record["data_type"]
            if str(data_type) == 'vod':
                pt = "0"
            else:
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(pt)
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # ln
        formatstring = collectArgs(formatstring, record, "ln", "lnerr", False, True)
        # cf
        formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        # definition
        try:
            definition = record["video_info"]["definition"]
            formatstring = formatstring + ',' + str(definition)
        except KeyError:
            formatstring = formatstring + ',-'

        # act
        formatstring = formatstring + ',' + 'play'

        # CLIENTTP
        try:
            clientver = record["apk_version"].lower()
            if 'apad' in clientver:
                clienttp = "apad"
            elif 'ipad' in clientver:
                clienttp = "ipad"
            elif 'aphone' in clientver:
                clienttp = 'android'
            elif 'iphone' in clientver:
                clienttp = 'iphone'
            else:
                write_to_file(("clienttperr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(clienttp)
        except KeyError:
            write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # CLIENTVER
        try:
            clientver = record["apk_version"].lower()
            if '.' in clientver:
                if "imgotv_aphone" in clientver:
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum == 0 or versionnum >= 452:
                        write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
                        return
                if "imgotv_iphone" in clientver:
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum == 0 or versionnum > 450:
                        write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
                        return

            formatstring = formatstring + ',' + str(clientver)
        except KeyError:
            write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
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
    # cat 201510110700_abc_log | python format_mpp_mobile.py ./genip 201510110700
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_mobile"
    for line in fileinput.input(sys.argv[3:]):
        mobile_format(line)
