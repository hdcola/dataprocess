#!/usr/bin/env python
# encoding: utf-8

from IPy import IP
import sys
import fileinput
import os
import time,datetime
import string

GEOIP = []
videoratemap = {''}
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
            GEOIP.append([rangmin, rangmax, country, province, city, operator])
        except ValueError, e:
            sys.stderr.write(("value error %s\n") % line)
    fp.close()

def getIpLocation(userip):
    userip = userip.strip('""')
    userip = IP(userip).int()
    for geoip in GEOIP:
      if userip >= geoip[0] and userip <= geoip[1] :
          return [geoip[2], geoip[3], geoip[4], geoip[5]]
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
    timetmp = timetmp.strip('""')
    timedata = time.strptime(timetmp,"%Y-%m-%dT%H:%M:%S+08:00")
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

def stripCdnLogFileLine(line):
    record = string.split(line, ',')
    logtype   = record[0]
    timetmp   = record[1]
    userip    = record[2]
    serverip  = record[3]
    datasize  = record[4]
    spendtime = record[5]
    url       = record[6]

    if datasize != 0 and spendtime != 0 and logtype != '\"3\"':
        iplocation = getIpLocation(userip)
        if iplocation == None:
            sys.stderr.write(("%s\n") % line)
            return
        videorate  = getVideoRate(url)
        if videorate == None:
            sys.stderr.write(("%s\n") % line)
            return
        timetmp =  formatTime(timetmp)
        operator = iplocation[3]
        province = iplocation[1]
    else:
        sys.stderr.write(("%s\n") % line)
        return
    serverlocation = 'NA'

    print "%s,%s,%s,%s,%s,%s,%s,%s" %(timetmp, userip.strip("\""),  \
        operator, province, serverip.strip("\""), serverlocation, \
        datasize.strip("\""), spendtime.strip("\""), videorate)


if __name__ == '__main__':
    # python cdncheck.py geoippath processfiles
    # gzcat abc.gz | python cdncheck.py ../geoip -
    # python cdncheck.py ../geoip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        stripCdnLogFileLine(line)
