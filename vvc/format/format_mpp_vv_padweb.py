#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file


def collectArgs(fstring, argslist, name, errname, strict, isNaN=False):
    try:
        nametmp = argslist[name]
        if strict:
            if str(nametmp).strip() == "":
                write_to_file(("%s,%s") % (errname, line), topic, log_time, start_time, "des_err")
                raise ValueError("args is illegal")
                return
            else:
                fstring = fstring + ',' + str(nametmp)
                return fstring
        else:
            fstring = fstring + ',' + str(nametmp)
            return fstring
    except KeyError:
        if isNaN:
            fstring = fstring + ',-'
            return fstring
        else:
            write_to_file(("%s,%s") % (errname, line), topic, log_time, start_time, "des_err")
            raise ValueError("args is illegal")
            return


def padweb_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return

    lineall = string.split(line.strip(), '\t')
    try:
        urlarg = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1].strip()
    except IndexError:
        write_to_file(("indexerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # date, time
    try:
        timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        log_time = timetmp_date + timetmp_time[:2] + "00"
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except (ValueError, KeyError):
        write_to_file(("timeerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # 写入时间正确的原始到orig文件
    write_to_file(line, topic, log_time, start_time, "orig")

    # IP
    try:
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        write_to_file(("iperr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except (ValueError, TypeError):
        write_to_file(("locationerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # url args
    try:
        urlargtmp = urlarg.split('&')
    except ValueError:
        write_to_file(("urlargerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    urlarglist = {}
    for urlargtmptmp in urlargtmp:
        try:
            argkey = urlargtmptmp.split('=')[0]
            argvalue = urlargtmptmp.split('=')[1]
            urlarglist[argkey] = argvalue
        except IndexError:
            write_to_file(("urlargerr,%s") % line, topic, log_time, start_time, "des_err")
            return

    # act提前校验
    try:
        act = urlarglist["act"]
        if str(act).strip() == "play":
            act = "play"
        elif str(act).strip() == "":
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        else:
            return
    except KeyError:
        write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
        return

    try:
        formatstring = collectArgs(formatstring, urlarglist, "uid", "uiderr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "uuid", "uuiderr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "guid", "guiderr", False, True)
        # ref
        formatstring = collectArgs(formatstring, urlarglist, "ref", "referr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "bid", "biderr", True)
        # cid
        formatstring = collectArgs(formatstring, urlarglist, "cid", "ciderr", False, True)
        # plid
        formatstring = collectArgs(formatstring, urlarglist, "plid", "pliderr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "vid", "viderr", True)
        try:
            tid = urlarglist["tid"]
            if tid.strip() == "":
                formatstring = formatstring + ','
            else:
                if tid.find(",") != -1:
                    tid = tid.replace(",", "_")
                formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ',-'

        # vts
        formatstring = collectArgs(formatstring, urlarglist, "vts", "vtserr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "cookie", "cookieerr", True)
        # pt
        try:
            bid = urlarglist['bid']
            if str(bid) == '4.0.3' or str(bid) == '4.1.1':
                pt = urlarglist['pt']
            else:
                pt = urlarglist['pt']
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # ln
        formatstring = collectArgs(formatstring, urlarglist, "ln", "lnerr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "cf", "cferr", False, True)
        # definition
        formatstring = collectArgs(formatstring, urlarglist, "def", "dererr", False, True)

        # act
        formatstring = formatstring + "," + str(act)

        # CLIENTTP
        formatstring = formatstring + ',' + "padweb"
        # aver
        formatstring = formatstring + ','
        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_padweb"
    for line in fileinput.input(sys.argv[3:]):
        padweb_format(line)
