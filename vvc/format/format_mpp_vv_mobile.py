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
    '''
    :param timetmp: 移动端时间为时间戳
    :return:
    '''
    try:
        timedata = time.localtime(timetmp)
    except ValueError:
        raise ValueError("timeerr")
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

def mobile_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = json.loads(line)
    except ValueError:
        sys.stderr.write(("jsonerr,%s") % line)
        return

    # date, time
    try:
        timetmp = record['time']
        timetmp_date, timetmp_time = formatTime(timetmp)
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError):
        sys.stderr.write(("timeerr,%s") % line)
        return

    # IP
    try:
        iptmp = record["ip"].strip()
        formatstring = formatstring + ',' + str(iptmp)
    except KeyError:
        sys.stderr.write(("iperr,%s") % line)
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except (ValueError, TypeError):
        sys.stderr.write(("locationerr,%s") % line)
        return

    clienttag = ""
    try:
        clientver = record["apk_version"].lower()
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
            elif versionnum < 452:
                clienttag = "aphonel452"
        elif clientver == "4.5.2":
            # 4.5.2属于新版，在旧版中丢掉
            clienttag = "aphone452"
            sys.stderr.write(("avererr,%s") % line)
            return
        else:
            clienttag = ""
    except KeyError:
        sys.stderr.write(("clienttypeerr,%s") % line)
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
                sys.stderr.write(("viderr,%s") % line)
                return
            formatstring = formatstring + ',' + str(vid)
        except KeyError:
            sys.stderr.write(("viderr,%s") % line)
            return

        # tid
        formatstring = collectArgs(formatstring, record, "tid", "tiderr", False, True)

        # vts
        formatstring = collectArgs(formatstring, record, "vts", "vtserr", False, True)
        # cookie
        try:
            cookie = record["mac"]
            if str(cookie).strip() == "":
                sys.stderr.write(("macerr,%s") % line)
                return
            formatstring = formatstring + ',' + str(cookie).lower()
        except KeyError:
            sys.stderr.write(("macerr,%s") % line)
            return
        # pt
        try:
            data_type = record["data_type"]
            if str(data_type) == 'vod':
                pt = "0"
            else:
                sys.stderr.write(("pterr,%s") % line)
                return
            formatstring = formatstring + ',' + str(pt)
        except KeyError:
            sys.stderr.write(("pterr,%s") % line)
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
                sys.stderr.write(("clienttypeerr,%s") % line)
                return
            formatstring = formatstring + ',' + str(clienttp)
        except KeyError:
            sys.stderr.write(("apk_versionerr,%s") % line)
            return

        # CLIENTVER
        try:
            clientver = record["apk_version"].lower()
            if '.' in clientver:
                if "imgotv_aphone" in clientver:
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum == 0 or versionnum >= 452:
                        sys.stderr.write(("apk_versionerr,%s") % line)
                        return
                if "imgotv_iphone" in clientver:
                    version = clientver.split('_')
                    versionnum = getVersionNum(version[2])
                    if versionnum == 0 or versionnum > 450:
                        sys.stderr.write(("apk_versionerr,%s") % line)
                        return
            else:
                formatstring = formatstring + ',' + str(clientver)
                # sys.stderr.write(("apk_versionerr,%s") % line)
                # return
            formatstring = formatstring + ',' + str(clientver)
        except KeyError:
            sys.stderr.write(("apk_versionerr,%s") % line)
            return
        print formatstring
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        mobile_format(line)
