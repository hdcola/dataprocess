#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
from pydota_common import formatLocation, loadGeoIp, formatTime, getVersionNum, write_to_file
import string
import urllib
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


def mobile_live_2011_20151105_format(line):
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

    try:
        recordall = json.loads(jsonline)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    try:
        record = recordall[0]
    except KeyError:
        record = recordall
    except TypeError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "orig_err")
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


    clienttag = ""
    try:
        clientver = record["aver"].lower()
        if "ipad" in clientver:
            clienttag = "ipad"
        elif "apad" in clientver:
            clienttag = "apad"
        elif "iphone" in clientver:
            version = clientver.split('_')
            if len(version) != 3:
                version = clientver.split('-')
            if len(version) == 3:
                versionnum = getVersionNum(version[2])
            else:
                write_to_file(("clientavererr,%s") % line, topic, log_time, start_time, "des_err")
            if versionnum < 454:
                clienttag = "iphonel454"
            elif versionnum >= 454:
                clienttag = "iphone454"
        elif "aphone" in clientver:
            version = clientver.split('_')
            if len(version) != 3:
                version = clientver.split('-')
            if len(version) == 3:
                versionnum = getVersionNum(version[2])
            else:
                write_to_file(("clientavererr,%s") % line, topic, log_time, start_time, "des_err")
            if versionnum < 452:
                clienttag = "aphonel452"
            elif versionnum >= 452:
                clienttag = "aphone452"
        elif clientver == "4.5.2":
            clienttag = "aphone452"
        else:
            clienttag = ""
    except KeyError:
        write_to_file(("clienttypeerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # pt 提前校验
    try:
        pt = record['pt']
        if str(pt) != '4':
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
    except KeyError:
        write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # act 提前校验
    act = ""
    if clienttag == "aphone452" or clienttag == "iphone454":
        try:
            act = record["act"]
            if act.strip() == "":
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            elif act == "aplay":
                act = 'play'
            else:
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
    elif clienttag == "aphonel452" or clienttag == "iphonel454":
        try:
            act = record["act"]
            if act.strip() == "":
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            elif act == "play":
                act = 'play'
            else:
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
    else:
        # ipad apad 以及一些无法解析的版本，同一按play过滤
        try:
            act = record["act"]
            if act.strip() == "":
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            elif act == "play":
                act = 'play'
            else:
                write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return

    # sourceid 提前校验
    try:
        lid = record["lid"]
        if str(lid) == "":
            write_to_file(("liderr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # if lid not in Meizi_info.keys():
        #     sys.stderr.write(("liderr,%s") % line)
        #     return
    except KeyError:
        write_to_file(("liderr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # live_infos = Meizi_info[lid]
    # isvalid, activityid, cameraid = CheckLiveTime(timeStamp, live_infos)
    #
    # if isvalid == -1:
    #     sys.stderr.write(("timeerr,%s") % line)
    #     return
    # elif isvalid == -2:
    #     sys.stderr.write(("overtimerr,%s") % line)
    #     return

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
        formatstring = formatstring + ','

        # plid
        formatstring = formatstring + ','

        # vid
        formatstring = formatstring + ','

        # tid
        formatstring = formatstring + ','

        # vts
        formatstring = formatstring + ','

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

        # cf
        formatstring = formatstring + ','
        # definition
        formatstring = collectArgs(formatstring, record, "def", "deferr", False, True)

        # act
        formatstring = formatstring + ',' + str(act)

        # CLIENTTP CLIENTVER
        try:
            clientver = record["aver"].lower()
            if 'iphone' in clientver:
                clienttp = 'iphone'
            elif 'apad' in clientver:
                clienttp = 'apad'
            elif 'ipad' in clientver:
                clienttp = 'ipad'
            else:
                clienttp = "android"

            formatstring = formatstring + ',' + str(clienttp)
            formatstring = formatstring + ',' + str(clientver)
        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        formatstring = formatstring + ',' + str(lid)

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
    topic = "mobile_live_2011_20151105"
    # Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        mobile_live_2011_20151105_format(line)
