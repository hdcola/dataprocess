#!/usr/bin/env python
# encoding: utf-8

"""
input 分格符为\t
pvid,ocvid,iid,log1,log2,log3,fast,srcid,ip,juid,ppid,pcnt,pscnt,adcnt,prcnt
pvid 页面id
ocvid 观看id
iid 节目id
log1 日志信息 只会有201
log2 代表事件信息，用“|”分隔，分别是起始播放点，当前播放点，下载点，总时长，码流。时间的单位为：秒
log3 时间戳
fast 飞速土豆版本号
srcid 播放器id
ip
juid 用户cookid
ppid 播放id
pcnt 观看行为计数
pscnt 播放行为子计数
adcnt 广告子计数
prcnt 201事件子计数

process
寻找唯一id中最后的播放时间点，统计出所有唯一次的播放时长数据

output
pvid,ocvid,iid,srcid,total,start,play
"""

import sys
import fileinput
import string

def dumplist(listdata):
  for key in listdata.keys():
    value = listdata[key]
    print "%s,%s" % (key,value)

def main(argv=None):
    adata={}
    for line in fileinput.input():
        pvid,ocvid,iid,log1,log2,log3,fast,srcid,ip,juid,ppid,pcnt,pscnt, \
            adcnt,prcnt=string.split(line[:-1],"\t")
        try:
        	start,play,download,total,bw=string.split(log2,"|")
        except ValueError, e:
        	sys.stderr.write(("log3 not include bw %s\n") % log2)
        playid = "%s,%s,%s,%s,%s,%s" % (pvid,ocvid,iid,srcid,total,start)
        if play > adata.get(playid,0) and adcnt!=0 :
            adata[playid]=play
    dumplist(adata)

if __name__ == "__main__":
    sys.exit(main())