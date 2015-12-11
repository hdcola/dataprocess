#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import urllib
import json
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


def ott_41_format(line):
    global log_time
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = json.loads(line)
    except ValueError:
        write_to_file(("jsonerr,%s") % line, topic, start_time, start_time, "orig_err")
        return

    # date, time
    try:
        timetmp = float(record['time'])
        timedata = time.localtime(timetmp)
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
        iptmp = record["ip"].strip()
        formatstring = formatstring + ',' + str(iptmp)
    except KeyError:
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
        formatstring = collectArgs(formatstring, record, "user_id", "user_iderr", False, True)
        # uuid
        try:
            uuid = record["play_session"]
            formatstring = formatstring + ',' + str(uuid)
        except KeyError:
            formatstring = formatstring + ',-'
        # guid
        formatstring = collectArgs(formatstring, record, "guid", "guiderr", False, True)
        # ref
        formatstring = collectArgs(formatstring, record, "ref", "referr", False, True)
        # bid
        formatstring = collectArgs(formatstring, record, "bid", "biderr", False, True)
        # cid
        try:
            cid = record["video_info"]['fstlvl_id']
            formatstring = formatstring + ',' + str(cid)
        except KeyError:
            formatstring = formatstring + ',-'

        # plid
        try:
            plid = record["video_info"]['sndlvl_id']
            formatstring = formatstring + ',' + str(plid)
        except KeyError:
            formatstring = formatstring + ',-'

        # vid
        try:
            vid = record["video_info"]['clip_id']
            if vid.strip() == "":
                write_to_file(("video_info.clip_iderr,%s") % line, topic, log_time, start_time, "des_err")
                return
            else:
                formatstring = formatstring + ',' + str(vid)
        except KeyError:
            write_to_file(("video_info.clip_iderr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # tid
        try:
            tid = record["video_info"]["tag"]
            if tid.strip() == "":
                formatstring = formatstring + ','
            else:
                if tid.find(",") != -1:
                    tid = tid.replace(",", "_")
                formatstring = formatstring + ',' + str(tid)
        except KeyError:
            formatstring = formatstring + ',-'

        # vts
        try:
            vts = record["video_info"]["epg_time"]
            formatstring = formatstring + ',' + str(vts)
        except KeyError:
            formatstring = formatstring + ',-'

        # cookie
        try:
            mac = record["mac"]
            if str(mac) == "":
                write_to_file(("macerr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(mac).lower()
        except KeyError:
            write_to_file(("macerr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # pt
        try:
            data_type = record["data_type"]
            if str(data_type) == 'vod':
                pt = "0"
            else:
                write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
                return
            formatstring = formatstring + ',' + str(pt)
        except KeyError:
            write_to_file(("pterr,%s") % line, topic, log_time, start_time, "des_err")
            return
        # ln
        formatstring = collectArgs(formatstring, record, "ln", "lnerr", False, True)
        # cf
        formatstring = collectArgs(formatstring, record, "cf", "cferr", False, True)
        # definition
        try:
            definition = record["video_info"]['definition']
            if str(definition).strip() == "":
                write_to_file(("video_info.definitionerr,%s") % line, topic, log_time, start_time, "des_err")
                return
            else:
                formatstring = formatstring + ',' + str(definition)
        except KeyError:
            formatstring = formatstring + ',－'

        # act
        formatstring = formatstring + ',' + 'play'
        # CLIENTTP
        formatstring = formatstring + ',' + "ott"
        # aver
        try:
            aver = str(record["apk_version"]).lower()
            if str(aver) == "":
                write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
                return
            aver_tmp = aver.split('.')
            if aver_tmp[5] == "dxjd" or aver_tmp[5] == "jllt" or aver_tmp[5] == "fjyd" \
                or aver_tmp[5] == "shyd19" or aver_tmp[0] == "yys":
                return
            formatstring = formatstring + ',' + str(aver).lower()
        except KeyError:
            write_to_file(("apk_versionerr,%s") % line, topic, log_time, start_time, "des_err")
            return

        # sourceid
        formatstring = formatstring + ','

        # cameraid
        formatstring = formatstring + ','
        # activityid
        formatstring = formatstring + ','

        # url
        try:
            url_str = record['url']
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
    topic = "ott_vv_41"
    for line in fileinput.input(sys.argv[3:]):
        ott_41_format(line)
