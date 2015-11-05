#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
from pydota_common import LoadLiveMeizi, CheckLiveTime, formatLocation, loadGeoIp, formatTime
import string
import urllib
import json

filesfps = []
filesfpscount = 0
Meizi_info = {}


def getVersionNum(verstr):
    try:
        vertmp = verstr.split('.')
        if len(vertmp) >= 3:
            return int(vertmp[0])*100+int(vertmp[1])*10+int(vertmp[2])
        else:
            return int(vertmp[0])*100+int(vertmp[1])*10
    except IndexError:
        return 0
    except ValueError:
        return 0


def collectArgs(fstring, argslist, name, errname, strict, isNaN=False):
    try:
        nametmp = argslist[name]
        if strict:
            if str(nametmp).strip() == "":
                sys.stderr.write(("%s,%s") % (errname, line))
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
            sys.stderr.write(("%s,%s") % (errname, line))
            raise ValueError("args is illegal")
            return


def rt_live_mobile_new_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    lineall = string.split(line.strip(), '\t')

    try:
        jsonline = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1].strip()
    except IndexError:
        sys.stderr.write(("indexerr,%s") % line)
        return

    try:
        recordall = json.loads(jsonline)
    except ValueError:
        sys.stderr.write(("jsonerr,%s") % line)
        return

    try:
        record = recordall[0]
    except KeyError:
        record = recordall


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
            if versionnum < 454:
                clienttag = "iphonel454"
            elif versionnum >= 454:
                clienttag = "iphone454"
        elif clientver == "4.5.2":
            clienttag = "aphone452"
        else:
            clienttag = "aphonel452"
    except KeyError:
        sys.stderr.write(("clienttypeerr,%s") % line)
        return

    # pt 提前校验
    try:
        pt = record['pt']
        if str(pt) != '4':
            sys.stderr.write(("pterr,%s") % line)
            return
    except KeyError:
        sys.stderr.write(("pterr,%s") % line)
        return

    # act 提前校验
    act = ""
    if clienttag == "aphone452" or clienttag == "iphone454":
        try:
            act = record["act"]
            if act.strip() == "":
                sys.stderr.write(("acterr,%s") % line)
                return
            elif act == "aplay":
                act = 'play'
            else:
                sys.stderr.write(("acterr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("acterr,%s") % line)
            return
    elif clienttag == "aphonel452" or clienttag == "iphonel454":
        try:
            act = record["act"]
            if act.strip() == "":
                sys.stderr.write(("acterr,%s") % line)
                return
            elif act == "play":
                act = 'play'
            else:
                sys.stderr.write(("acterr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("acterr,%s") % line)
            return
    else:
        return

    # sourceid 提前校验
    try:
        lid = record["lid"]
        if str(lid) == "":
            sys.stderr.write(("liderr,%s") % line)
            return
        if lid not in Meizi_info.keys():
            sys.stderr.write(("liderr,%s") % line)
            return
    except KeyError:
        sys.stderr.write(("liderr,%s") % line)
        return

    # date, time
    try:
        timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError):
        sys.stderr.write(("timeerr,%s") % line)
        return

    live_infos = Meizi_info[lid]
    isvalid, activityid, cameraid = CheckLiveTime(timeStamp, live_infos)

    if isvalid == -1:
        sys.stderr.write(("timeerr,%s") % line)
        return
    elif isvalid == -2:
        sys.stderr.write(("overtimerr,%s") % line)
        return

    # IP
    try:
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        sys.stderr.write(("iperr,%s") % line)
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except ValueError:
        sys.stderr.write(("locationerr,%s") % line)
        return
    except TypeError:
        sys.stderr.write(("locationerr,%s") % line)
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
                sys.stderr.write(("diderr,%s") % line)
                return
            formatstring = formatstring + ',' + str(cookie).lower()
        except KeyError:
            sys.stderr.write(("diderr,%s") % line)
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
            else:
                clienttp = 'android'
            formatstring = formatstring + ',' + str(clienttp)
            formatstring = formatstring + ',' + str(clientver)
        except KeyError:
            sys.stderr.write(("avererr,%s") % line)
            return

        formatstring = formatstring + ',' + str(lid)

        # cameraid
        formatstring = formatstring + ',' + str(cameraid)
        # activityid
        formatstring = formatstring + ',' + str(activityid)

        print formatstring
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        rt_live_mobile_new_format(line)
