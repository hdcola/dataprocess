#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file, getVersionNum, check_act_field
import json


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


def mobile_new_version_format(line):
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

    if not check_act_field(jsonline, "play", "aplay"):
        write_to_file("acterr,", topic, log_time, start_time, "des_err")
        return

    try:
        recordall = json.loads(jsonline)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "des_err")
        return

    try:
        record = recordall[0]
    except KeyError:
        record = recordall

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

    clienttag = ""
    try:
        clientver = record["aver"].lower()
        if "ipad" in clientver:
            clienttag = "ipad"
        elif "apad" in clientver:
            clienttag = "apad"
        elif "imgotv_iphone" in clientver:
            version = clientver.split('_')
            versionnum = getVersionNum(version[2])
            if 450 <= versionnum <= 453:
                clienttag = "iphone450453"
            elif versionnum < 450:
                clienttag = "iphonel450"
            elif versionnum >= 454:
                clienttag = "iphone454"
        elif "imgotv_aphone" in clientver:
            version = clientver.split('_')
            versionnum = getVersionNum(version[2])
            if versionnum >= 452:
                clienttag = "aphone452"
            else:
                clienttag = "aphonel452"
        elif str(clientver).startswith("aphone"):
            clienttag = "aphoneother"
        elif clientver == "4.5.2":
            clienttag = "aphone452"
        else:
            clienttag = ""
    except KeyError:
        write_to_file(("clienttypeerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # act
    act = ""
    if clienttag == "aphone452" or clienttag == "iphone454":
        try:
            act = record["act"]
            if act.strip() == "":
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            elif act.strip() == "aplay":
                act = "play"
            else:
                return
        except KeyError:
            write_to_file("acterr,", topic, log_time, start_time, "des_err")
            return
    elif clienttag == "iphone450453" or clienttag == "aphoneother":
        for i in range(len(recordall)):
            try:
                if recordall[i]["act"] == "play":
                    act = "play"
                    break
            except KeyError:
                continue
        if act.strip() == "":
            return
    else:
        try:
            act = record["act"]
            if act.strip() == "":
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            elif act.strip() == "aplay":
                act = "play"
            else:
                return
        except KeyError:
            write_to_file("acterr,", topic, log_time, start_time, "des_err")
            return

    try:
        # iphone 4.5.0以后的版本，未登陆，没uid相关字段。
        # uid
        # if clienttag in ("aphone452", "iphone450453", "iphone454"):
        formatstring = collectArgs(formatstring, record, "uid", "uiderr", False, True)

        # uuid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)

        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)

        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)

        # bid

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
        try:
            pt = record['pt']
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # ln
        formatstring = collectArgs(formatstring, record, "ln", "lnerr", False, True)
        # cf
        formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        # definition
        formatstring = collectArgs(formatstring, record, "def", "deferr", False, True)

        # act
        formatstring = formatstring + ',' + str(act)

        # CLIENTTP
        try:
            clientver = record["aver"].lower()
            if 'iphone' in clientver:
                clienttp = 'iphone'
            else:
                clienttp = 'android'
            formatstring = formatstring + ',' + str(clienttp)
        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # CLIENTVER
        try:
            clientver = record["aver"].lower()
            if "imgotv_iphone" in clientver:
                if act == 'play':
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if 450 <= versionnum:
                        formatstring = formatstring + ',' + str(clientver)
                    else:
                        write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                        return
                else:
                    write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            elif "imgotv_aphone" in clientver:
                if act == "play":
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum >= 452:
                        formatstring = formatstring + ',' + str(clientver)
                    else:
                        write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                        return
                else:
                    write_to_file(("playreperr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            elif str(clientver).startswith("aphone"):
                if act == 'play':
                    formatstring = formatstring + ',' + str(clientver)
                else:
                    write_to_file(("playreperr,%s") % line, topic, log_time, start_time, "des_err")
                    return
            else:
                if act == 'play':
                    versionnum = getVersionNum(clientver)
                    if versionnum >= 452:
                        formatstring = formatstring + ',' + str(clientver)
                    else:
                        write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
                        return
                else:
                    write_to_file(("playreperr,%s") % line, topic, log_time, start_time, "des_err")
                    return

        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return
        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_mobile_new_version"
    for line in fileinput.input(sys.argv[3:]):
        mobile_new_version_format(line)
