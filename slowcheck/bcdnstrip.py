#!/usr/bin/env python
# encoding: utf-8

'''
处理bcdn节点数据，将一个数据文件中出现过一次的慢速请求的独立用户都标记为慢速,并按独立用户去重

源数据
201508302400,110.52.142.39,联通,湖南,36.250.93.31,网宿,3111,1,900,0
201508302400,110.252.53.163,联通,河北,121.17.124.14,网宿,545117,736,900,0
201508302400,171.104.56.151,电信,广西,222.216.188.65,网宿,3061,1,900,0
201508302400,122.77.158.219,铁通,陕西,111.20.250.32,网宿,606915,63,900,0
201508302400,122.77.158.219,铁通,陕西,111.20.250.32,网宿,606915,6328,900,1
结果数据
201508302400,110.52.142.39,联通,湖南,36.250.93.31,网宿,3111,1,900,0
201508302400,110.252.53.163,联通,河北,121.17.124.14,网宿,545117,736,900,0
201508302400,171.104.56.151,电信,广西,222.216.188.65,网宿,3061,1,900,0
201508302400,122.77.158.219,铁通,陕西,111.20.250.32,网宿,606915,6328,900,1


err数据类型
indexerr 数据列不够

使用
python bcdnstrip.py [ files | - ]
'''

import sys
import fileinput
import string
import gzip

SLOWUSER  = {}
def loadSlowUser(filename):
    if filename.endswith('gz'):
        fp = gzip.open(filename)
    else:
        fp  = open(filename)
    for i, line in enumerate(fp):
        try:
            record = string.split(line, ",")
            userip     = record[1]
            slowstatus = record[9]
            if int(slowstatus) == 1 :
                SLOWUSER[userip] = 1
        except ValueError:
            sys.stderr.write(("indexerr,%s") % line)
    fp.close()

def stripBcdnLogFileLine(filename):
    if filename.endswith('gz'):
        fp = gzip.open(filename)
    else:
        fp  = open(filename)

    for i, line in enumerate(fp):
        record = string.split(line, ",")
        userip     = record[1]
        try:
            if SLOWUSER[userip] == 1:
                SLOWUSER[userip] = 0
                print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(record[0],record[1],
                    record[2], record[3], record[4], record[5], record[6],
                    record[7], record[8], 1)
        except KeyError:
            SLOWUSER[userip] = 0
            print line
    fp.close()

if __name__ == '__main__':
    filename = sys.argv[1]
    loadSlowUser(filename)
    stripBcdnLogFileLine(filename)
