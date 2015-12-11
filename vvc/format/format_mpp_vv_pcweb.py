#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import urllib
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


def pcp_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = string.split(line, '- -')
        recordtmp = record[1].strip().split(' ')
        timetmp = str(recordtmp[0]) + str(recordtmp[1])
    except IndexError:
        write_to_file(("indexerr,%s") % line, topic, start_time, start_time, "orig_err")
        return
    # date, time
    try:
        timedata = time.strptime(timetmp, "[%d/%b/%Y:%H:%M:%S+0800]")
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        log_time = timetmp_date + timetmp_time[:2] + "00"
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except ValueError:
        write_to_file(("timeerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # 写入时间正确的原始到orig文件
    write_to_file(line, topic, log_time, start_time, "orig")

    # IP
    try:
        iptmp = record[0].strip().split(',')
        if len(iptmp) != 1:
            write_to_file(("iperr,%s") % line, topic, log_time, start_time, "des_err")
            return
        else:
            formatstring = formatstring + ',' + str(iptmp[0])
    except IndexError:
            write_to_file(("iperr,%s") % line, topic, log_time, start_time, "des_err")
            return

    # location
    try:
        locationtmp = formatLocation(iptmp[0])
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except ValueError:
        write_to_file(("locationerr,%s") % line, topic, log_time, start_time, "des_err")
        return
    except TypeError:
        write_to_file(("locationerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    # url args
    try:
        urlargtmp = record[1].strip().split(' ')[3].split('?')[1].split('&')
    except (ValueError, IndexError):
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
        try:
            ref = urlarglist['ref']
            if ref.strip() == "":
                formatstring = formatstring + ','
            else:
                ref = urllib.unquote(ref)
                if ref.find(",") != -1:
                    ref = ref.replace(",", "")
                formatstring = formatstring + ',' + str(ref)
        except KeyError:
            formatstring = formatstring + ',-'

        formatstring = collectArgs(formatstring, urlarglist, "bid", "biderr", True)
        formatstring = collectArgs(formatstring, urlarglist, "cid", "ciderr", False, True)
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

        formatstring = collectArgs(formatstring, urlarglist, "vts", "vtserr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "cookie", "cookieerr", True)
        # pt
        try:
            bid = urlarglist['bid']
            tp = urlarglist['tp']
            if str(bid) == '1' and str(tp) == '1':
                pt = '0'
            else:
                pt = urlarglist['pt']
            formatstring = formatstring + ',' + str(pt)
            if str(pt) != '0':
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        formatstring = collectArgs(formatstring, urlarglist, "ln", "lnerr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "cf", "cferr", False, True)
        formatstring = collectArgs(formatstring, urlarglist, "definition", "definitionerr", False, True)
        # act
        formatstring = formatstring + "," + str(act)
        # CLIENTTP
        formatstring = formatstring + ',' + "pcweb"
        # aver
        formatstring = formatstring + ','

        # sourceid
        formatstring = formatstring + ','

        # cameraid
        formatstring = formatstring + ','
        # activityid
        formatstring = formatstring + ','

        # url
        try:
            url_str = urlarglist['url']
            if url_str.strip() == "":
                formatstring = formatstring + ','
            else:
                url_str = urllib.unquote(url_str)
                if url_str.find(",") != -1:
                    url_str = url_str.replace(",", "")
                formatstring = formatstring + ',' + str(url_str)
        except KeyError:
            formatstring = formatstring + ',-'

        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mpp_vv_pcweb"
    for line in fileinput.input(sys.argv[3:]):
        pcp_format(line)
