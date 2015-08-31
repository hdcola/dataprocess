#!/usr/bin/env python
# encoding: utf-8

from IPy import IP
import sys
import fileinput
import os
import time,datetime
import string

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
            sys.stderr.write(("value error %s\n") % line)
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

def getIpLocation(userip):
    userip = userip.strip('""')
    userip = IP(userip).int()
    location = getRangeKey(userip)
    if location and GEOIP[location]:
        if location <= userip <= GEOIP[location][0]:
            return GEOIP[location]
    else:
        return None

def getVideoRate(url):
    url = string.split(url, 'id=')
    if len(url) >= 2:
        url = string.split(url[1], '&')
    else:
        return None

    id = url[0]
    return id

def formatTime(timetmp):
    timedata = time.strptime(timetmp,"[%d/%b/%Y:%H:%M:%S +0800]")
    tm_min = timedata.tm_min / 5 * 5 + 5
    tm_hour = timedata.tm_hour
    if tm_min == 60:
        tm_min = '00'
        tm_hour = timedata.tm_hour + 1
    if tm_min < 10:
        tm_min = '0'+str(tm_min)
    if tm_hour < 10:
        tm_hour = '0'+str(tm_hour)
    timetmp = time.strftime('%Y%m%d', timedata)+str(tm_hour)+str(tm_min)
    return timetmp

def stripBcdnLogFileLine(line):
    record         = line.split('\"')
    try:
       ipandtime      = record[0].split(' - - ')
       userip         = ipandtime[0]
       timetmp        = ipandtime[1]
       timetmp        = timetmp.strip()
       timetmp        = formatTime(timetmp)
       iplocation     = getIpLocation(userip)
       operator       = iplocation[4]
       province       = iplocation[2]
       serverip       = record[6].strip().split(' ')[1]
       videorate      = record[1].split('/')
       videorate      = videorate[len(videorate)-2].split(' ')[0]
       datasize       = record[2].strip().split(' ')[1]
       spendtime      = record[6].strip().split(' ')[0]
       serverlocation = 'NA'
    except IndexError :
        sys.stderr.write(("%s\n") % line)
        return
    print "%s,%s,%s,%s,%s,%s,%s,%s,%s" %(timetmp,
        userip.strip("\""), operator, province,
        serverip.strip("\""), serverlocation,
        datasize.strip("\""), spendtime.strip("\""), videorate)


if __name__ == '__main__':
    # python cdncheck.py geoippath processfiles
    # gzcat abc.gz | python cdncheck.py ../geoip -
    # python cdncheck.py ../geoip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        stripBcdnLogFileLine(line)
