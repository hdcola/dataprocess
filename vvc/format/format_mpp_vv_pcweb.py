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
    try:
        timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
    except ValueError:
        raise ValueError("timeerr")
    timetmp_date = time.strftime('%Y%m%d', timedata)
    timetmp_time = time.strftime('%H%M%S', timedata)
    return timetmp_date, timetmp_time

def pcp_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = string.split(line, '- -')
        recordtmp = record[1].strip().split(' ')
        timetmp = str(recordtmp[0]) + str(recordtmp[1])
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
    # IP
    try:
        iptmp = record[0].strip().split(',')
        if len(iptmp) != 1:
            sys.stderr.write(("iperr,%s") % line)
            return
        else:
            formatstring = formatstring + ',' + str(iptmp[0])
    except IndexError:
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
    # url args
    try:
        urlargtmp = record[1].strip().split(' ')[3].split('?')[1].split('&')
    except ValueError or IndexError:
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
    # uid
    try:
        uid = urlarglist['uid']
        formatstring = formatstring + ',' + str(uid)
    except KeyError:
        sys.stderr.write(("uiderr,%s") % line)
        return

    # uuid
    try:
        uuid = urlarglist['uuid']
        formatstring = formatstring + ',' + str(uuid)
    except KeyError:
        sys.stderr.write(("uuiderr,%s") % line)
        return
    # guid
    try:
        guid = urlarglist['guid']
        formatstring = formatstring + ',' + str(guid)
    except KeyError:
        sys.stderr.write(("guiderr,%s") % line)
        return
    # ref
    try:
        ref = urlarglist['ref']
        ref = urllib.unquote(ref)
        formatstring = formatstring + ',' + str(ref)
    except KeyError:
        sys.stderr.write(("referr,%s") % line)
        return
    # bid
    try:
        bid = urlarglist['bid']
        formatstring = formatstring + ',' + str(bid)
    except KeyError:
        sys.stderr.write(("biderr,%s") % line)
        return
    # cid
    try:
        cid = urlarglist['cid']
        formatstring = formatstring + ',' + str(cid)
    except KeyError:
        sys.stderr.write(("ciderr,%s") % line)
        return
    # plid
    try:
        plid = urlarglist['plid']
        formatstring = formatstring + ',' + str(plid)
    except KeyError:
        sys.stderr.write(("pliderr,%s") % line)
        return
    # vid
    try:
        vid = urlarglist['vid']
        formatstring = formatstring + ',' + str(vid)
    except KeyError:
        sys.stderr.write(("viderr,%s") % line)
        return
    # tid
    try:
        tid = urlarglist['tid']
        formatstring = formatstring + ',' + str(tid)
    except KeyError:
        sys.stderr.write(("tiderr,%s") % line)
        return
    # vts
    try:
        vts = urlarglist['vts']
        formatstring = formatstring + ',' + str(vts)
    except KeyError:
        sys.stderr.write(("vtserr,%s") % line)
        return

    # cookie or DID
    try:
        cookie = urlarglist['cookie']
        formatstring = formatstring + ',' + str(cookie)
    except KeyError:
        sys.stderr.write(("cookieerr,%s") % line)
        return
    # pt
    try:
        tp = urlarglist['tp']
        if str(bid) == '1' and str(tp) == '1':
            pt = '0'
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
    try:
        ln = urlarglist['ln']
        formatstring = formatstring + ',' + str(ln)
    except KeyError:
        sys.stderr.write(("lnerr,%s") % line)
        return
    # cf
    try:
        cf = urlarglist['cf']
        formatstring = formatstring + ',' + str(cf)
    except KeyError:
        sys.stderr.write(("cferr,%s") % line)
        return
    # definition
    try:
        definition = urlarglist['definition']
        formatstring = formatstring + ',' + str(definition)
    except KeyError:
        sys.stderr.write(("definitionerr,%s") % line)
        return
    # act
    try:
        act = urlarglist['act']
        formatstring = formatstring + ',' + str(act)
    except KeyError:
        sys.stderr.write(("acterr,%s") % line)
        return
    # CLIENTTP
    clienttp = "pcweb"
    formatstring = formatstring + ',' + str(clienttp)

    # CLIENTVER
    try:
        clientver = urlarglist["aver"]
        formatstring = formatstring + ',' + str(clientver)
    except KeyError:
        clientver = ""
        formatstring = formatstring + ',' + str(clientver)

    print formatstring

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        pcp_format(line)
