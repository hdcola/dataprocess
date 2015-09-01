#!/usr/bin/env python
# encoding: utf-8

'''
处理cdn节点数据

源数据
"1","2015-08-27T20:15:25+08:00","42.198.139.35","111.161.8.41","629048","218","http://111.161.8.41:8080/nn_live.ts?nea=%26nn_time_len%3d0&id=wmjq_mzb1_mpp_hd&nn_m3u8=1&nn_file_index=288135543&nn_file_name=20150827T121500Z&nn_file_index_time=1440677715&nn_file_start=1813448&nn_file_end=2442496&nn_ak=01686df8ed1518de6a36ba319ac2163b46&nal=0101ffde550607997c3238de5c3624371b56dee8e930b7&nn_user_id=0&nn_device_id=10&ngs=55deff010006d8e848123796c05a3b6a&ncmsid=13001004&nes=678a358cdf270a6ff7d5cb231a9e5024&nn_time_len=0","hlv","10","200","OK","wmjq_mzb1_mpp_hd",""

结果数据
111.8.134.147,移动,湖南,111.8.4.235,NA,629048,152,wmjq_mzb1_mpp_hd

err数据
indexerr 数据列不够
useriperr ip地址不对
serveriperr ip地址不对
videorateerr 视频区间不对
timeerr 时间不对

使用
python cdncheck.py geoip文件路径 idcinfo文件路径 [ files | - ]
'''

from videoratelist import VIDEORATELIST
from IPy import IP
import sys
import fileinput
import time
import string

GEOIP_SORT = []
GEOIP  = {}
IDCINFO = {}
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
            GEOIP[rangmin] = [rangmax, country, province, city, operator]
            GEOIP_SORT.append(rangmin)
        except ValueError:
            sys.stderr.write(("geoerr,%s") % line)
    GEOIP_SORT.sort()
    fp.close()

def loadIdcInfo(filename):
    fp  = open(filename)
    for i, line in enumerate(fp):
        try:
            record = string.split(line, ",")
            location = record[4]
            serverip = record[5].strip().split(' ')
            if len(serverip) > 1:
                for i in range(0, len(serverip)):
                    IDCINFO[serverip[i]] = location
            else:
                IDCINFO[serverip[0]] = location

        except ValueError:
            sys.stderr.write(("idcerr,%s") % line)
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

def getServerLocation(serverip):
    serverip = serverip.strip('"')
    location = IDCINFO[serverip]
    return location

def getVideoRate(url):
    url = string.split(url, 'id=')
    if len(url) >= 2:
        url = string.split(url[1], '&')
    else:
        return None

    id = url[0]
    try:
        videorate = VIDEORATELIST[id]
    except KeyError as e:
        videorate = 2*1000
    return videorate

def genSlowResult(datasize, spendtime, videorate):
  spendtime = int(spendtime.strip('""'))
  datasize = int(datasize.strip('""'))

  if(spendtime==0 or datasize==0):
      raise ValueError("size or data is zero")

  videorate = int(videorate)
  # datasize 单位为B
  # spendtime 单位为ms
  # videorate 单位为Kbps
  if int(spendtime) != 0:
    realrate = datasize*8/spendtime
    if realrate >= videorate:
        return 0
    else:
        return 1
  else:
    return 0

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
    try:
        logtype   = record[0]
        timetmp   = record[1]
        userip    = record[2]
        serverip  = record[3]
        datasize  = record[4]
        spendtime = record[5]
        url       = record[6]
    except IndexError as e:
        sys.stderr.write(("indexerr,%s") % line)
        return

    if datasize != 0 and spendtime != 0 and logtype != '\"3\"':
        try:
            iplocation = getIpLocation(userip)
        except ValueError as e:
            sys.stderr.write(("useriperr,%s") % line)
            return

        videorate  = getVideoRate(url)
        if videorate == None:
            sys.stderr.write(("videorateerr,%s") % line)
            return

        try:
            timetmp =  formatTime(timetmp)
        except ValueError as e:
            sys.stderr.write(("timeerr,%s") % line)

        operator = iplocation[4]
        province = iplocation[2]
        try:
            serverlocation = getServerLocation(serverip)
        except KeyError as e:
            sys.stderr.write(("serveriperr,%s") % line)
            return
        try:
            slowResult = genSlowResult(datasize, spendtime, videorate)
        except ValueError as e:
            sys.stderr.write(("zeroerr,%s") % line)
            return
    else:
        sys.stderr.write(("pass,%s") % line)
        return

    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(timetmp, userip.strip('"'),
        operator, province, serverip.strip('"'), serverlocation,
        datasize.strip('"'), spendtime.strip('"'), videorate, slowResult)


if __name__ == '__main__':
    # python cdncheck.py geoippath idcinfopath processfiles
    # gzcat abc.gz | python cdncheck.py ../geoip  ../idcinfo -
    # python cdncheck.py ../geoip ./idcinfo afile bfile cfile
    loadGeoIp(sys.argv[1])
    loadIdcInfo(sys.argv[2])
    for line in fileinput.input(sys.argv[3:]):
        stripCdnLogFileLine(line)
