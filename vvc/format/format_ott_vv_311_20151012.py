#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import json
import urllib
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

def ott_vv_311_20151012_format(line):
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
        locationtmp = formatLocation(iptmp[0])
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
        # uid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False)
        # uuid
        formatstring = collectArgs(formatstring, record, "suuid", "suuiderr", True)
        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", True)
        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False)
        # bid
        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        # cid
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False)
        # plid
        formatstring = collectArgs(formatstring, record, "oplid", "opliderr", False)
        # vid
        formatstring = collectArgs(formatstring, record, "ovid", "oviderr", True)
        # tid
        formatstring = collectArgs(formatstring, record, "tid", "tiderr", False)
        # vts
        formatstring = collectArgs(formatstring, record, "vts", "vtserr", True)
        # cookie
        formatstring = collectArgs(formatstring, record, "did", "diderr", True)
        # pt
        formatstring = formatstring + ',' + '0'
        # ln
        formatstring = formatstring + ','
        # cf
        formatstring = collectArgs(formatstring, record, "cf", "cferr", True)
        # definition
        formatstring = collectArgs(formatstring, record, "def", "deferr", True)
        # act
        formatstring = collectArgs(formatstring, record, "act", "acterr", True)
        # CLIENTTP
        formatstring = formatstring + ',' + "ott"
        # aver
        formatstring = collectArgs(formatstring, record, "aver", "avererr", True)
        print formatstring.lower()
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        ott_vv_311_20151012_format(line)
