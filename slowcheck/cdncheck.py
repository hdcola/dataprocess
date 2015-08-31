#!/usr/bin/env python
# encoding: utf-8

from IPy import IP
import sys
import fileinput
import os
import string

GEOIP = []
videoratemap = {''}
def loadGeoIp(data_dir, filename):
    filename = os.path.join(data_dir, filename)
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
    url = string.split(url, '&id=')
    if len(url) >= 2:
        url = string.split(url[1], '&')
    else:
        return None

    id = url[0]
    return id

def stripCdnLogFileLine(line):
    record = string.split(line, ',')
    logtype   = record[0]
    userip    = record[2]
    serverip  = record[3]
    datasize  = record[4]
    spendtime = record[5]
    url       = record[6]
    iplocation = getIpLocation(userip)
    videorate  = getVideoRate(url)
    if iplocation and videorate and datasize != 0 and spendtime != 0 and logtype != '\"3\"':
        operator = iplocation[3]
        province = iplocation[1]
    else:
        sys.stderr.write(("%s\n") % line)
        return
    serverlocation = 'NA'

    print "%s,%s,%s,%s,%s,%s,%s,%s" %(userip, operator, province, serverip, serverlocation, datasize, spendtime, videorate)


if __name__ == '__main__':
    loadGeoIp('./', 'geoip')
    for line in fileinput.input():
        stripCdnLogFileLine(line)
