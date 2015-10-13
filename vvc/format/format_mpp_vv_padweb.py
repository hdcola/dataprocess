#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
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

def padweb_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return

    lineall = string.split(line.strip(), '\t')
    try:
        urlarg = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1]
    except IndexError:
        sys.stderr.write(("indexerr,%s") % line)
        return

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

    # url args
    try:
        urlargtmp = urlarg.split('&')
    except ValueError:
        sys.stderr.write(("urlargerr,%s") % line)
        return

    urlarglist = {}
    for urlargtmptmp in urlargtmp:
        try:
            argkey = urlargtmptmp.split('=')[0]
            argvalue = urlargtmptmp.split('=')[1]
            urlarglist[argkey] = argvalue
        except IndexError:
            sys.stderr.write(("urlargerr,%s") % line)
            return

    try:
        formatstring = collectArgs(formatstring, urlarglist, "uid", "uiderr", False)
        formatstring = collectArgs(formatstring, urlarglist, "uuid", "uuiderr", True)
        formatstring = collectArgs(formatstring, urlarglist, "guid", "guiderr", True)
        # ref
        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, urlarglist, "bid", "biderr", True)
        # cid
        formatstring = formatstring + ','
        # plid
        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, urlarglist, "vid", "viderr", True)
        formatstring = collectArgs(formatstring, urlarglist, "tid", "tiderr", True)
        # vts
        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, urlarglist, "cookie", "cookieerr", True)
        # pt
        try:
            bid = urlarglist['bid']
            if str(bid) == '4.0.3' or str(bid) == '4.1.1':
                pt = urlarglist['pt']
            else:
                pt = urlarglist['pt']
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                sys.stderr.write(("pterr,%s") % line)
                return
        except KeyError:
            sys.stderr.write(("pterr,%s") % line)
            return

        # ln
        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, urlarglist, "cf", "cferr", True)
        # definition
        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, urlarglist, "act", "acterr", True)
        # CLIENTTP
        formatstring = formatstring + ',' + "padweb"
        # aver
        formatstring = formatstring + ','
        print formatstring.lower()
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        padweb_format(line)
