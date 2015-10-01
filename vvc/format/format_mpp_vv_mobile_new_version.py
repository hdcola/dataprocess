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

def mobile_new_version_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    lineall = string.split(line.strip(), '\t')
    try:
        jsonline = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1]
    except IndexError:
        sys.stderr.write(("indexerr,%s") % line)
        return
    try:
        record = json.loads(jsonline)
    except ValueError:
        sys.stderr.write(("jsonerr,%s") % line)
        return
    try:
        record = record[0]
    except KeyError:
        record = record

    # date, time
    try:
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

    # uid
    try:
        uid = record['uid']
        formatstring = formatstring + ',' + str(uid)
    except KeyError:
        #uid = ""
        #formatstring = formatstring + ',' + str(uid)
        sys.stderr.write(("uiderr,%s") % line)
        return

    # uuid
    try:
        uuid = record['uuid']
        formatstring = formatstring + ',' + str(uuid)
    except KeyError:
        #uuid = ""
        #formatstring = formatstring + ',' + str(uuid)
        sys.stderr.write(("uuiderr,%s") % line)
        return

    # guid
    try:
        guid = record['guid']
        formatstring = formatstring + ',' + str(guid)
    except KeyError:
        #guid = ""
        #formatstring = formatstring + ',' + str(guid)
        sys.stderr.write(("guiderr,%s") % line)
        return

    # ref
    try:
        ref = record['ref']
        #ref = urllib.unquote(ref)
        formatstring = formatstring + ',' + str(ref)
    except KeyError:
        #ref = ""
        #ref = urllib.unquote(ref)
        #formatstring = formatstring + ',' + str(ref)
        sys.stderr.write(("referr,%s") % line)
        return

    # bid
    try:
        bid = record['bid']
        formatstring = formatstring + ',' + str(bid)
    except KeyError:
        #bid = ""
        #formatstring = formatstring + ',' + str(bid)
        sys.stderr.write(("biderr,%s") % line)
        return

    # cid
    try:
        cid = record['cid']
        formatstring = formatstring + ',' + str(cid)
    except KeyError:
        #cid = ""
        #formatstring = formatstring + ',' + str(cid)
        sys.stderr.write(("ciderr,%s") % line)
        return

    # plid
    try:
        plid = record['plid']
        formatstring = formatstring + ',' + str(plid)
    except KeyError:
        #plid = ""
        #formatstring = formatstring + ',' + str(plid)
        sys.stderr.write(("plid,%s") % line)
        return

    # vid
    try:
        vid = record['vid']
        formatstring = formatstring + ',' + str(vid)
    except KeyError:
        sys.stderr.write(("viderr,%s") % line)
        return

    # tid
    try:
        tid = record['tid']
        formatstring = formatstring + ',' + str(tid)
    except KeyError:
        #tid = ""
        #formatstring = formatstring + ',' + str(tid)
        sys.stderr.write(("tiderr,%s") % line)
        return

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
        pt = record['pt']
        formatstring = formatstring + ',' + str(pt)
        if str(pt) != '0':
            sys.stderr.write(("pterr,%s") % line)
            return
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
        definition = record['definition']
        formatstring = formatstring + ',' + str(definition)
    except KeyError:
        definition = ""
        formatstring = formatstring + ',' + str(definition)
    # act
    try:
        act = record['act']
        formatstring = formatstring + ',' + str(act)
    except KeyError:
        #act = ""
        #formatstring = formatstring + ',' + str(act)
        sys.stderr.write(("acterr,%s") % line)
        return

    # CLIENTTP
    clienttp = "mobile"
    formatstring = formatstring + ',' + str(clienttp)

    # CLIENTVER
    try:
        clientver = record["aver"]
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
        mobile_new_version_format(line)
