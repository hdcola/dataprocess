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
    try:
        timedata = time.localtime(timetmp)
    except ValueError:
        raise ValueError("timeerr")
    timetmp_date = time.strftime('%Y%m%d', timedata)
    timetmp_time = time.strftime('%H%M%S', timedata)
    return timetmp_date, timetmp_time

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
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)
        return
    except KeyError:
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
    except ValueError:
        sys.stderr.write(("locationerr,%s") % line)
        return

    # uid
    try:
        uid = record['user_id']
        formatstring = formatstring + ',' + str(uid)
    except KeyError:
        uid = ""
        formatstring = formatstring + ',' + str(uid)

    # uuid
    try:
        uuid = record['uuid']
        formatstring = formatstring + ',' + str(uuid)
    except KeyError:
        uuid = ""
        formatstring = formatstring + ',' + str(uuid)

    # guid
    try:
        guid = record['guid']
        formatstring = formatstring + ',' + str(guid)
    except KeyError:
        guid = ""
        formatstring = formatstring + ',' + str(guid)

    # ref
    try:
        ref = record['ref']
        ref = urllib.unquote(ref)
        formatstring = formatstring + ',' + str(ref)
    except KeyError:
        ref = ""
        ref = urllib.unquote(ref)
        formatstring = formatstring + ',' + str(ref)

    # bid
    try:
        bid = record['bid']
        formatstring = formatstring + ',' + str(bid)
    except KeyError:
        bid = ""
        formatstring = formatstring + ',' + str(bid)

    # cid
    try:
        cid = record['cid']
        formatstring = formatstring + ',' + str(cid)
    except KeyError:
        cid = ""
        formatstring = formatstring + ',' + str(cid)

    # plid
    try:
        plid = record['plid']
        formatstring = formatstring + ',' + str(plid)
    except KeyError:
        plid = ""
        formatstring = formatstring + ',' + str(plid)

    # vid
    try:
        vid = record["video_info"]['video_id']
        formatstring = formatstring + ',' + str(vid)
    except KeyError:
        sys.stderr.write(("viderr,%s") % line)
        return

    # tid
    try:
        tid = record['tid']
        formatstring = formatstring + ',' + str(tid)
    except KeyError:
        tid = ""
        formatstring = formatstring + ',' + str(tid)

    # vts
    try:
        vts = record['vts']
        formatstring = formatstring + ',' + str(vts)
    except KeyError:
        vts = ""
        formatstring = formatstring + ',' + str(vts)

    # cookie or DID or mac
    try:
        cookie = record['did']
        formatstring = formatstring + ',' + str(cookie)
    except KeyError:
        try:
            cookie = record['mac']
            formatstring = formatstring + ',' + str(cookie)
        except KeyError:
            try:
                cookie = record['cookie']
                formatstring = formatstring + ',' + str(cookie)
            except KeyError:
                sys.stderr.write(("cookieerr,%s") % line)
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
    try:
        ln = record['ln']
        formatstring = formatstring + ',' + str(ln)
    except KeyError:
        ln = ""
        formatstring = formatstring + ',' + str(ln)

    # cf
    try:
        cf = record['cf']
        formatstring = formatstring + ',' + str(cf)
    except KeyError:
        cf = ""
        formatstring = formatstring + ',' + str(cf)
    # definition
    try:
        definition = record['video_info']['definition']
        formatstring = formatstring + ',' + str(definition)
    except KeyError:
        sys.stderr.write(("definitionerr,%s") % line)
        return
    # act
    try:
        act = record['act']
        formatstring = formatstring + ',' + str(act)
    except KeyError:
        act = ""
        formatstring = formatstring + ',' + str(act)

    # CLIENTTP
    clienttp = "mobile"
    formatstring = formatstring + ',' + str(clienttp)

    # CLIENTVER
    try:
        clientver = record["apk_version"]
        formatstring = formatstring + ',' + str(clientver)
    except KeyError:
        sys.stderr.write(("clientvererr,%s") % line)
        return
    print formatstring

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        mobile_format(line)
