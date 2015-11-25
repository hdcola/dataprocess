#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file
import string
import urllib
import time


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


def pcweb_pv_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return

    lineall = string.split(line.strip(), '\t')
    try:
        recordtmp = lineall[7].strip()
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


    recordtmp = recordtmp.strip().split('&')

    record = {}
    for recordtmptmp in recordtmp:
        try:
            argkey = recordtmptmp.split('=')[0]
            argvalue = recordtmptmp.split('=')[1]
            record[argkey] = argvalue
        except IndexError:
            write_to_file(("recorderr,%s") % line, topic, start_time, start_time, "des_err")
            return

    # act提前校验
    try:
        act = record["act"]
        if str(act).strip() == "pv":
            act = "pv"
        elif str(act).strip() == "":
            write_to_file(("acterr,%s") % line, topic, start_time, start_time, "des_err")
            return
        else:
            return
    except KeyError:
        write_to_file(("acterr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # IP
    try:
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        write_to_file(("iperr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except (ValueError, TypeError):
        write_to_file(("locationerr,%s") % line, topic, start_time, start_time, "des_err")
        return

    try:
        formatstring = collectArgs(formatstring, record, "uid", "uiderr", False, True)
        formatstring = collectArgs(formatstring, record, "suuid", "suuiderr", False, True)
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)
        # ref
        try:
            ref = record['ref']
            if ref.strip() == "":
                formatstring = formatstring + ','
            else:
                ref = urllib.unquote(ref)
                if ref.find(",") != -1:
                    ref = ref.replace(",", "")
                formatstring = formatstring + ',' + str(ref)
        except KeyError:
            formatstring = formatstring + ',-'

        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)
        # cid plid vid置空
        formatstring = collectArgs(formatstring, record, "cid", "ciderr", False, True)
        formatstring = collectArgs(formatstring, record, "plid", "pliderr", False, True)
        formatstring = collectArgs(formatstring, record, "vid", "viderr", False, True)

        # url
        try:
            url_re = record['url']
            if url_re.strip() == "":
                formatstring = formatstring + ','
            else:
                url_re = urllib.unquote(url_re)
                if url_re.find(",") != -1:
                    url_re = url_re.replace(",", "")
                formatstring = formatstring + ',' + str(url_re)
        except KeyError:
            formatstring = formatstring + ',-'

        # ch
        formatstring = collectArgs(formatstring, record, "ch", "cherr", False, True)

        formatstring = collectArgs(formatstring, record, "cookie", "cookieerr", False, True)

        # pt os
        formatstring = collectArgs(formatstring, record, "pt", "pterr", False, True)
        formatstring = collectArgs(formatstring, record, "os", "oserr", False, True)

        # wuid pix
        formatstring = collectArgs(formatstring, record, "wuid", "wuiderr", False, True)
        formatstring = collectArgs(formatstring, record, "pix", "pixerr", False, True)

        # act
        formatstring = formatstring + "," + str(act)

        # CLIENTTP
        formatstring = formatstring + ",pcweb"

        # CLIENTVER TYPE MF MOD
        formatstring = formatstring + ','
        formatstring = formatstring + ','
        formatstring = formatstring + ','
        formatstring = formatstring + ','


        # SOPLID SOVID
        formatstring = collectArgs(formatstring, record, "soplid", "sopliderr", False, True)
        formatstring = collectArgs(formatstring, record, "sovid", "sovid", False, True)

        # NET
        formatstring = formatstring + ','

        # EXT1 EXT2 EXT3
        formatstring = collectArgs(formatstring, record, "ext1", "ext1err", False, True)
        formatstring = collectArgs(formatstring, record, "ext2", "ext2err", False, True)
        formatstring = collectArgs(formatstring, record, "ext3", "ext3err", False, True)

        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "pcweb_pv"
    # Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        pcweb_pv_format(line)
