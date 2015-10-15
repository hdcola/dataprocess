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

def mobile_new_version_211_20151012_format(line):
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

    try:

        #uid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False)
        #uuid
        formatstring = collectArgs(formatstring, record, "suuid", "suiderr", True)

        formatstring = collectArgs(formatstring, record, "guid", "guiderr", True)

        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False)
        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False)

        #plid
        formatstring = collectArgs(formatstring, record, "plid", "pliderr", False)

        formatstring = collectArgs(formatstring, record, "vid", "viderr", True)

        # tid
        try:
            tid = record["tid"]
            formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ','

        # vts
        formatstring = formatstring + ','
        # cookie
        formatstring = collectArgs(formatstring, record, "did", "diderr", False)
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
        formatstring = collectArgs(formatstring, record, "def", "deferr", False)

        # act
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
            if "imgotv-aphone" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 453:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    sys.stderr.write(("avererr,%s") % line)
                    return
            elif "imgotv-iphone" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 455:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    sys.stderr.write(("avererr,%s") % line)
                    return
            elif "ipad" in clientver:
                version = clientver.split('-')
                versionnum = getVersionNum(version[2])
                if versionnum >= 423:
                    formatstring = formatstring + ',' + str(clientver).lower()
                else:
                    sys.stderr.write(("avererr,%s") % line)
                    return
            else:
                sys.stderr.write(("avererr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("avererr,%s") % line)
            return
        print formatstring.lower()
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        mobile_new_version_211_20151012_format(line)
