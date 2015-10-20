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

def ott_44_format(line):
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
    except TypeError:
        sys.stderr.write(("locationerr,%s") % line)
        return

    # act提前校验
    try:
        act = record["act"]
        if str(act).strip() == "play":
            act = "play"
        elif str(act).strip() == "":
            sys.stderr.write(("acterr,%s") % line)
            return
        else:
            return
    except KeyError:
        sys.stderr.write(("acterr,%s") % line)
        return

    try:
        # uid
        formatstring = collectArgs(formatstring, record, "uid", "uiderr", False, True)
        # uuid
        formatstring = collectArgs(formatstring, record, "bg_uuid", "bg_uuiderr", False, True)
        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)
        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)
        # bid
        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        # cid
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False, True)
        # plid
        formatstring = collectArgs(formatstring, record, "oplid", "opliderr", False, True)
        # vid
        formatstring = collectArgs(formatstring, record, "ovid", "oviderr", True)
        # tid
        try:
            tid = record["tid"]
            formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ',-'

        # vts
        formatstring = collectArgs(formatstring, record, "vts", "vtserr", False, True)
        # cookie
        try:
            did = record["did"]
            if str(did) == "":
                sys.stderr.write(("diderr,%s") % line)
                return
            formatstring = formatstring + ',' + str(did).lower()
        except KeyError:
            sys.stderr.write(("diderr,%s") % line)
            return
        # pt
        try:
            bid = record["bid"]
            pt = record["pt"]
            if str(bid) == '3.0.1' and str(pt) == '1':
                pt = '0'
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                sys.stderr.write(("pterr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("pterr,%s") % line)
            return
        # ln
        formatstring = collectArgs(formatstring, record, "ln", "lnerr", False, True)
        # cf
        formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        # definition
        formatstring = collectArgs(formatstring, record, "def", "deferr", False, True)
        # act
        formatstring = formatstring + "," + str(act)
        # CLIENTTP
        formatstring = formatstring + ',' + "ott"
        # aver
        try:
            aver = str(record["aver"]).lower()
            if str(aver) == "":
                sys.stderr.write(("avererr,%s") % line)
                return
            aver_tmp = aver.split('.')
            if aver_tmp[5] == "dxjd" or aver_tmp[5] == "jllt" or aver_tmp[5] == "fjyd" \
                or aver_tmp[5] == "shyd19" or aver_tmp[0] == "yys":
                return
            formatstring = formatstring + ',' + str(aver).lower()
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
        ott_44_format(line)
