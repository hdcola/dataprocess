#!/usr/bin/env python
# encoding: utf-8

import sys
import time
import string
import bz2


def getTimeHour(timetmp):
    timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
    tm_hour = timedata.tm_hour
    if tm_hour < 10:
        tm_hour = '0'+str(tm_hour)
    return tm_hour

def genCsvFileName(reportdir, stime):
    return str(reportdir)+"/"+str(clienttype)+"_"+str(stime)+"_vv_"+str(count_type)+"_hour.csv"

def genCsvTimeName():
    return str(start_time_hour)

def formatTime(timetmp):
    timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
    timeStamp = int(time.mktime(timedata))
    return timeStamp

def sortRecord(filename, ctype):
    global start_time_day
    global start_time_hour
    if filename.endswith('bz2'):
        fp = bz2.BZ2File(filename)
    else:
        fp  = open(filename)

    for i, line in enumerate(fp):
        try:
            record = string.split(line, ",")
            datetmp = record[0]
            timetmp = record[1]
            timetmptmp = str(datetmp)+str(timetmp)
            if start_time_hour == 0:
                start_time_hour = getTimeHour(timetmptmp)
            if start_time_day == 0:
                start_time_day = str(datetmp)

            if ctype == "pl":
                typetmp = record[11]
            elif ctype == "chn":
                tptmp   = record[16]
                if tptmp != "0":
                    continue
                else:
                    typetmp = record[10]
            else:
                typetmp = "all"
                acttmp = record[20]
                if acttmp != "play":
                    continue

            if typetmp == "":
                typetmp = "NaN"
            try:
                SORTRECORD[typetmp] += 1
            except IndexError:
                SORTRECORD[typetmp] = 1
            except KeyError:
                SORTRECORD[typetmp] = 1
        except IndexError:
            sys.stderr.write(("indexerr,%s") % line)
    fp.close()


def count_vv(filename, ctype, reportdir):
    sortRecord(filename, ctype)
    for (k, v) in SORTRECORD.items():
        csvfilename = genCsvFileName(reportdir, start_time_day)
        csvtimename = genCsvTimeName()
        cfp  = open(csvfilename, 'a+')
        constr = str(start_time_day) + "," + str(csvtimename) + "," + str(k) + "," + str(v) + "\n"
        cfp.write(constr)
        cfp.close()

if __name__ == '__main__':
    # gzcat abc.gz | python count_vv.py clienttype "all" -
    # python count_vv.py clienttype "all" afile bfile cfile
    global SORTRECORD
    global start_time_hour
    global start_time_day
    global clienttype
    start_time_day = 0
    start_time_hour = 0
    SORTRECORD = {}
    try:
        clienttype = sys.argv[1]
    except IndexError:
        clienttype = ""
    count_type = sys.argv[2]
    filename = sys.argv[3]
    reportdir = sys.argv[4]
    count_vv(filename, count_type, reportdir)
