#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file
import string
import urllib
import time

# Meizi_info = {}


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


def rt_live_pcweb_format(line):
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
        if str(act).strip() == "play":
            act = "play"
        elif str(act).strip() == "":
            write_to_file(("acterr,%s") % line, topic, start_time, start_time, "des_err")
            return
        else:
            return
    except KeyError:
        write_to_file(("acterr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # pt提前校验
    try:
        pt = record["pt"]
        if str(pt) != '4':
            write_to_file(("pterr,%s") % line, topic, start_time, start_time, "des_err")
            return
    except KeyError:
        write_to_file(("pterr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # sourceid 提前校验
    try:
        lid = record["lid"]
        if str(lid) == "":
            write_to_file(("liderr,%s") % line, topic, start_time, start_time, "des_err")
            return
        # if lid not in Meizi_info.keys():
        #     sys.stderr.write(("liderr,%s") % line)
        #     return
    except KeyError:
        write_to_file(("liderr,%s") % line, topic, start_time, start_time, "des_err")
        return

    # live_infos = Meizi_info[lid]
    # isvalid, activityid, cameraid = CheckLiveTime(timeStamp, live_infos)
    #
    # if isvalid == -1:
    #     sys.stderr.write(("timeerr,%s") % line)
    #     return
    # elif isvalid == -2:
    #     sys.stderr.write(("overtimerr,%s") % line)
    #     return


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
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)
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
        # cid plid vid tid vts置空
        formatstring = formatstring + ','
        formatstring = formatstring + ','
        formatstring = formatstring + ','
        formatstring = formatstring + ','
        formatstring = formatstring + ','

        formatstring = collectArgs(formatstring, record, "cookie", "cookieerr", True)

        # pt
        formatstring = formatstring + ',' + str(pt)

        try:
            ln = record['ln']
            if ln.strip() == "":
                formatstring = formatstring + ','
            else:
                ln = urllib.unquote(ln)
                formatstring = formatstring + ',' + str(ln)
        except KeyError:
            formatstring = formatstring + ',-'

        formatstring = formatstring + ','
        formatstring = collectArgs(formatstring, record, "definition", "definitionerr", False, True)
        # act
        formatstring = formatstring + "," + str(act)

        # CLIENTTP
        try:
            platform = record["platform"]
            if str(platform) == "1":
                clienttp = "pcclient"
            elif str(platform) == "0":
                clienttp = "pcweb"
            else:
                write_to_file(("platformerr,%s") % line, topic, start_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + clienttp
        except KeyError:
            write_to_file(("platformerr,%s") % line, topic, start_time, start_time, "des_err")
            return

        # aver
        formatstring = formatstring + ','

        # liveid
        formatstring = formatstring + ',' + str(lid)

        # cameraid
        formatstring = formatstring + ','
        # activityid
        formatstring = formatstring + ','
        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "rt_live_pcweb"
    # Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        rt_live_pcweb_format(line)
