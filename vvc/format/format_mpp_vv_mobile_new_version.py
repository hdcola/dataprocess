#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import urllib
import json
from IPy import IP

filesfps = []
filesfpscount = 0
GEOIP_SORT = []
GEOIP  = {}

def loadGeoIp(filename):
    fp  = open(filename)
    for i, line in enumerate(fp):
        try:
            record = string.split(line, "\t")
            rangmin  = record[0]
            rangmax  = record[1]
            country  = record[2]
            province = record[3]
            city     = record[4]
            operator = record[6]
            rangmin = IP(rangmin).int()
            rangmax = IP(rangmax).int()
            GEOIP[rangmin] = [rangmax, country, province, city, operator]
            GEOIP_SORT.append(rangmin)
        except ValueError:
            sys.stderr.write(("value error,%s") % line)
    GEOIP_SORT.sort()
    fp.close()

def getRangeKey(userip):
    low = 0
    height = len(GEOIP_SORT)-1
    while low < height:
        mid = (low+height)/2
        if GEOIP_SORT[mid] < userip and GEOIP_SORT[mid + 1] < userip:
            low = mid + 1
        elif GEOIP_SORT[mid] > userip and GEOIP_SORT[mid - 1] > userip:
            height = mid - 1
        elif GEOIP_SORT[mid] <= userip and GEOIP_SORT[mid +1] > userip:
            return GEOIP_SORT[mid]
        elif GEOIP_SORT[mid -1] <= userip and GEOIP_SORT[mid] > userip:
            return GEOIP_SORT[mid -1]
        elif GEOIP_SORT[mid + 1] == userip:
            return GEOIP_SORT[mid +1]
        else:
            return None
    return None

def formatLocation(userip):
    userip = userip.strip('""')
    userip = IP(userip).int()
    location = getRangeKey(userip)
    if location and GEOIP[location]:
        if location <= userip <= GEOIP[location][0]:
            return GEOIP[location]
    else:
        return None

def formatTime(timetmp):
    timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
    timetmp_date = time.strftime('%Y%m%d', timedata)
    timetmp_time = time.strftime('%H%M%S', timedata)
    return timetmp_date, timetmp_time

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

def collectArgs(fstring, argslist, name, errname, strict):
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
        sys.stderr.write(("%s,%s") % (errname, line))
        raise ValueError("args is illegal")
        return

def mobile_new_version_format(line):
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

    # date, time
    try:
        timetmp_date, timetmp_time = formatTime(timetmp)
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError):
        sys.stderr.write(("timeerr,%s") % line)
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
        elif clientver == "4.5.2":
            clienttag = "aphone452"
        else:
            clienttag = ""
    except KeyError:
        sys.stderr.write(("clienttypeerr,%s") % line)
        return

    try:
        # iphone 4.5.0以后的版本，未登陆，没uid相关字段。
        # uid
        # if clienttag in ("aphone452", "iphone450453", "iphone454"):
        if clienttag == "aphone452":
            formatstring = collectArgs(formatstring, record, "uid", "uiderr", False)
        elif clienttag == "iphone450453" or clienttag == "iphone454":
            try:
                uid = record["uid"]
                formatstring = formatstring + ',' + str(uid)
            except KeyError:
                formatstring = formatstring + ','
        else:
            formatstring = formatstring + ','

        # uuid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", True)
        else:
            formatstring = formatstring + ','

        # guid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "guid", "guiderr", True)
        else:
            formatstring = formatstring + ','

        # ref
        formatstring = formatstring + ','

        # bid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        else:
            formatstring = formatstring + ','

        # cid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "cid", "ciderr", False)
        else:
            formatstring = formatstring + ','

        # plid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "plid","pliderr", False)
        else:
            formatstring = formatstring + ','

        # vid
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "vid", "viderr", True)
        else:
            formatstring = formatstring + ','

        # tid
        try:
            tid = record["tid"]
            formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ','

        # vts
        formatstring = formatstring + ','

        # cookie
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "did", "diderr", False)
        else:
            formatstring = formatstring + ','

        # pt
        try:
            pt = record['pt']
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                sys.stderr.write(("pterr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("pterr,%s") % line)
            return
        # ln
        formatstring = formatstring + ','
        # cf
        formatstring = formatstring + ','
        # definition
        if clienttag == "aphone452" or clienttag == "iphone450453" or clienttag == "iphone454":
            formatstring = collectArgs(formatstring, record, "def", "definitionerr", False)
        else:
            formatstring = formatstring + ','

        # act
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
                formatstring = formatstring + ',' + str(act)
            except KeyError:
                sys.stderr.write(("acterr,%s") % line)
                return
        elif clienttag == "iphone450453":
            for i in range(len(recordall)):
                try:
                    if recordall[i]["act"] == "play":
                        act = "play"
                        break
                except KeyError:
                    continue
            if act.strip() == "":
                sys.stderr.write(("acterr,%s") % line)
                return
            else:
                formatstring = formatstring + ',' + str(act)
        else:
            formatstring = formatstring + ',' + 'play'


        # CLIENTTP
        try:
            clientver = record["aver"].lower()
            if 'iphone' in clientver:
                clienttp = 'iphone'
            else:
                clienttp = 'android'
            formatstring = formatstring + ',' + str(clienttp)
        except KeyError:
            sys.stderr.write(("avererr,%s") % line)
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
                        sys.stderr.write(("avererr,%s") % line)
                        return
                # elif act == 'aplay':
                #     version = clientver.split('_')
                #     versionnum = getVersionNum(version[2])
                #     if versionnum >= 453:
                #         formatstring = formatstring + ',' + str(clientver)
                #     else:
                #         sys.stderr.write(("playreperr,%s") % line)
                #         return
                else:
                    sys.stderr.write(("acterr,%s") % line)
                    return
            elif "imgotv_aphone" in clientver:
                if act == "play":
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum >= 452:
                        formatstring = formatstring + ',' + str(clientver)
                    else:
                        sys.stderr.write(("avererr,%s") % line)
                        return
                else:
                    sys.stderr.write(("playreperr,%s") % line)
                    return
            else:
                if act == 'play':
                    versionnum = getVersionNum(clientver)
                    if versionnum >= 452:
                        formatstring = formatstring + ',' + str(clientver)
                    else:
                        sys.stderr.write(("avererr,%s") % line)
                        return
                else:
                    sys.stderr.write(("playreperr,%s") % line)
                    return

            # act = record["act"]
            # clientver = record["aver"].lower()
            # if "imgotv_iphone" in clientver:
            #     if act == 'play':
            #         version = clientver.split('_')
            #         versionnum = getVersionNum(version[2])
            #         if versionnum >= 450 or versionnum <= 453:
            #             formatstring = formatstring + ',' + str(clientver)
            #         else:
            #             sys.stderr.write(("avererr,%s") % line)
            #             return
            #     elif act == 'aplay':
            #         version = clientver.split('_')
            #         versionnum = getVersionNum(version[2])
            #         if versionnum >= 453:
            #             formatstring = formatstring + ',' + str(clientver)
            #         else:
            #             sys.stderr.write(("playreperr,%s") % line)
            #             return
            #     else:
            #         sys.stderr.write(("acterr,%s") % line)
            #         return
            # elif "imgotv_aphone" in clientver:
            #     if act == "aplay":
            #         version = clientver.split('_')
            #         versionnum = getVersionNum(version[2])
            #         if versionnum >= 452:
            #             formatstring = formatstring + ',' + str(clientver)
            #         else:
            #             sys.stderr.write(("avererr,%s") % line)
            #             return
            #     else:
            #         sys.stderr.write(("playreperr,%s") % line)
            #         return
            # else:
            #     if act == 'aplay':
            #         versionnum = getVersionNum(clientver)
            #         if versionnum >= 452:
            #             formatstring = formatstring + ',' + str(clientver)
            #         else:
            #             sys.stderr.write(("avererr,%s") % line)
            #             return
            #     else:
            #         sys.stderr.write(("playreperr,%s") % line)
            #         return
        except KeyError:
            sys.stderr.write(("avererr,%s") % line)
            return
        print formatstring
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        mobile_new_version_format(line)
