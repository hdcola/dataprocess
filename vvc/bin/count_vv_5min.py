#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import bz2

CSV_TIMELIST = [":00", ":05", ":10", ":15", ":20", ":25",
                ":30", ":35",":40", ":45", ":50",":55", ":55"]

def getTimeHour(timetmp):
    timedata = time.strptime(timetmp,"%Y%m%d%H:%M:%S")
    tm_hour = timedata.tm_hour
    if tm_hour < 10:
        tm_hour = '0'+str(tm_hour)
    return tm_hour

def formatTime(timetmp):
    timedata = time.strptime(timetmp,"%Y%m%d%H:%M:%S")
    timeStamp = int(time.mktime(timedata))
    return timeStamp

def sortRecord(filename, ctype):
    global start_time
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
            timetmp = formatTime(timetmptmp)
            if start_time_hour == 0:
                start_time_hour = getTimeHour(timetmptmp)
            if start_time == 0:
                start_time = formatTime(str(datetmp) + str(start_time_hour) + ":00:00")

            if ctype == "pl":
                typetmp = record[11]
            elif ctype == "chn":
                tptmp   = record[16]
                if tptmp != "1":
                    continue
                else:
                    typetmp = record[10]
            else:
                typetmp = "all"

            if typetmp == "":
                typetmp = "NaN"

            try:
                count = SORTRECORD[timetmp][2] + 1
            except IndexError:
                count = 0
            except KeyError:
                count = 0

            SORTRECORD[timetmp] = [datetmp, typetmp, count]
        except IndexError:
            sys.stderr.write(("indexerr,%s") % line)
    fp.close()

def genCsvFileName(reportdir, stime):
    return str(reportdir)+"/"+str(clienttype)+"."+str(stime)+".vv."+str(count_type)+".5min.csv"

def genCsvTimeName(scount):
    return str(start_time_hour) + CSV_TIMELIST[int(scount)]

def count_vv(filename, ctype):
    sortRecord(filename, ctype)
    mincount = 0
    count = 1
    for (k,v) in  sorted(SORTRECORD.items(), key=lambda d: d[0]):
        mincount_tmp = (k - start_time) / 300
        if mincount == mincount_tmp:
            if v[1] == "all":
                count += v[2]
            else:

                try:
                    SORTRECORD1[v[1]] += 1
                except IndexError:
                    SORTRECORD1[v[1]] = 1
                except KeyError:
                    SORTRECORD1[v[1]] = 1
        else:
            csvfilename = genCsvFileName(reportdir, v[0])
            csvtimename = genCsvTimeName(mincount)
            cfp  = open(csvfilename, 'a+')
            if count != 1:
                constr = str(v[0]) + "," + str(csvtimename) + "," + str(v[1]) + "," + str(count) + "\n"
                cfp.write(constr)
                cfp.close()
            else:
                for (k1, v1) in SORTRECORD1.items():
                    print k1
                    constr = str(v[0]) + "," + str(csvtimename) + "," + str(v[1]) + "," + str(v1) + "\n"
                    cfp.write(constr)
                    SORTRECORD1[k1] = 0
                cfp.close()
            count = 0
            mincount += 1

if __name__ == '__main__':
    # python count_vv.py clienttype "all" afile bfile cfile
    global SORTRECORD
    global SORTRECORD1
    global start_time
    global start_time_hour
    global clienttype
    start_time = 0
    start_time_hour = 0
    SORTRECORD = {}
    SORTRECORD1 = {}
    try:
        clienttype = sys.argv[1]
    except IndexError:
        clienttype = ""
    count_type = sys.argv[2]
    filename = sys.argv[3]
    reportdir = sys.argv[4]
    count_vv(filename, count_type, reportdir)
