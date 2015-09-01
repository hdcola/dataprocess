#!/usr/bin/env python
# encoding: utf-8

'''
处理bcdn节点数据

源数据
182.115.237.195 - - [27/Aug/2015:20:00:00 +0800] "GET http://phonehuodong.imgo.tv/nn_live/nn_x64/aWQ9d21qcV9temIxX21wcF9oZCZjZG5leF9pZD13c19waG9uZV9saXZlJm5uX3RpbWVfbGVuPTA,/wmjq_mzb1_mpp_hd.m3u8 HTTP/1.1" 200 3101 "-" "ArcSoft Player 1.0" 0 61.163.117.12

结果数据
201508272005,182.115.237.195,联通,河南,61.163.117.12,NA,3101,0,wmjq_mzb1_mpp_hd.m3u8

err数据类型
indexerr 数据列不够
iperr ip地址不对
videorateerr 视频区间不对
timeerr 时间不对
rateerr 速率计算不对

使用
python bcdncheck.py geoip文件路径 bcdnname [ files | - ]
'''

from videoratelist import VIDEORATELIST
from IPy import IP
import sys
import fileinput
import time
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

def getIpLocation(userip):
    userip = userip.strip('""')
    userip = IP(userip).int()
    location = getRangeKey(userip)
    if location and GEOIP[location]:
        if location <= userip <= GEOIP[location][0]:
            return GEOIP[location]
    else:
        return None

def getVideoRate(videorateid):
    try:
        videorate = VIDEORATELIST[videorateid]
    except KeyError as e:
        videorate = 2*1000
    return videorate

def genSlowResult(datasize, spendtime, videorate):
    spendtime = int(spendtime.strip('""'))
    datasize = int(datasize.strip('""'))
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
       videorate      = videorate[len(videorate)-2].split(' ')[0].split('.')[0]
       datasize       = record[2].strip().split(' ')[1]
       spendtime      = record[6].strip().split(' ')[0]
       videorate  =  getVideoRate(videorate)
       try:
           slowResult     = genSlowResult(datasize, spendtime, videorate)
       except ValueError as e:
           sys.stderr.write(("rate,%s") % line)
           return
    except IndexError :
        sys.stderr.write(("indexerr,%s") % line)
        return
    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(timetmp,
        userip.strip("\""), operator, province,
        serverip.strip("\""), serverlocation,
        datasize.strip("\""), spendtime.strip("\""), videorate, slowResult)


if __name__ == '__main__':
    # python cdncheck.py geoippath processfiles
    # gzcat abc.gz | python cdncheck.py ../geoip bcdnname -
    # python cdncheck.py ../geoip bcdnname afile bfile cfile
    loadGeoIp(sys.argv[1])
    global serverlocation
    serverlocation = sys.argv[2]
    for line in fileinput.input(sys.argv[3:]):
        stripBcdnLogFileLine(line)
