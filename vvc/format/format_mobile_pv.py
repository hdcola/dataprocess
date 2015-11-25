#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
from pydota_common import formatLocation, loadGeoIp, formatTime, write_to_file, check_act_field
import string
import json

reload(sys)
sys.setdefaultencoding('utf-8')


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


def mobile_pv_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    lineall = string.split(line.strip(), '\t')

    try:
        jsonline = lineall[7].strip()
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

    if not check_act_field(jsonline, "pv"):
        write_to_file("acterr,", topic, log_time, start_time, "des_err")
        return

    try:
        recordall = json.loads(jsonline)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, log_time, start_time, "des_err")
        return

    try:
        record = recordall[0]
    except KeyError:
        record = recordall

    # act 提前校验
    act = ""
    try:
        act = record["act"]
        if act.strip() == "":
            write_to_file(("acterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        elif act.strip() == "pv":
            act = "pv"
        else:
            return
    except KeyError:
        write_to_file("acterr,", topic, log_time, start_time, "des_err")
        return

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

    try:
        # uid
        formatstring = collectArgs(formatstring, record, "uuid", "uuiderr", False, True)

        # uuid
        formatstring = formatstring + ",-"

        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)

        # ref
        formatstring = formatstring + ",-"

        # bid
        formatstring = collectArgs(formatstring, record, "bid", "biderr", True)

        # cid
        formatstring = formatstring + ',-'

        # plid
        formatstring = formatstring + ',-'

        # vid
        formatstring = formatstring + ',-'

        # url
        formatstring = formatstring + ',-'

        # ch
        formatstring = collectArgs(formatstring, record, "ch", "cherr", False, True)

        # cookie
        try:
            cookie = record["did"]
            if str(cookie).strip() == "":
                write_to_file(("diderr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(cookie).lower()
        except KeyError:
            write_to_file(("diderr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # pt
        formatstring = collectArgs(formatstring, record, "desc", "descerr", False, True)

        # os
        formatstring = collectArgs(formatstring, record, "sver", "svererr", False, True)

        # wuid pix
        formatstring = formatstring + ",-"
        formatstring = formatstring + ",-"

        # act
        formatstring = formatstring + ',' + str(act)

        # CLIENTTP CLIENTVER
        try:
            clientver = record["aver"].lower()
            if 'iphone' in clientver:
                clienttp = 'iphone'
            elif 'apad' in clientver:
                clienttp = 'apad'
            elif 'ipad' in clientver:
                clienttp = 'ipad'
            else:
                clienttp = "android"

            formatstring = formatstring + ',' + str(clienttp)
            formatstring = formatstring + ',' + str(clientver)
        except KeyError:
            write_to_file(("avererr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # type
        formatstring = collectArgs(formatstring, record, "type", "typeerr", False, True)

        # mf
        formatstring = collectArgs(formatstring, record, "mf", "mferr", False, True)

        # mod
        formatstring = collectArgs(formatstring, record, "mod", "moderr", False, True)

        # SOPLID SOVID
        formatstring = formatstring + ",-"
        formatstring = formatstring + ",-"

        # NET
        formatstring = collectArgs(formatstring, record, "net", "neterr", False, True)

        # EXT1 EXT2 EXT3
        formatstring = formatstring + ",-"
        formatstring = formatstring + ",-"
        formatstring = formatstring + ",-"

        write_to_file(formatstring, topic, log_time, start_time, "des")
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    topic = "mobile_pv"
    # Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        mobile_pv_format(line)
