#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
from pydota_common import LoadLiveMeizi, CheckLiveTime, formatLocation, loadGeoIp, formatTime
import string
import urllib
import time

filesfps = []
filesfpscount = 0
Meizi_info = {}


def collectArgs(fstring, argslist, name, errname, strict, isNaN=False):
    try:
        nametmp = argslist[name]
        if strict:
            if str(nametmp).strip() == "":
                sys.stderr.write(("%s,%s") % (errname, line))
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
            sys.stderr.write(("%s,%s") % (errname, line))
            raise ValueError("args is illegal")
            return


def rt_live_pcweb_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return

    lineall = string.split(line.strip(), '\t')
    try:
        recordtmp = lineall[7].strip()
        timetmp  = lineall[0]
        iptmp  = lineall[1].strip()
    except IndexError:
        sys.stderr.write(("indexerr,%s") % line)
        return

    recordtmp = recordtmp.strip().split('&')

    record = {}
    for recordtmptmp in recordtmp:
        try:
            argkey = recordtmptmp.split('=')[0]
            argvalue = recordtmptmp.split('=')[1]
            record[argkey] = argvalue
        except IndexError:
            sys.stderr.write(("recorderr,%s") % line)
            return

    # act提前校验
    try:
        act = record["act"]
        if str(act).strip() == "play":
            act = "play"
        elif str(act).strip() == "":
            sys.stderr.write(("acterr,%s") % line)
            return
        else:
            return
    except KeyError:
        sys.stderr.write(("acterr,%s") % line)
        return

    # pt提前校验
    try:
        pt = record["pt"]
        if str(pt) != '4':
            sys.stderr.write(("pterr,%s") % line)
            return
    except KeyError:
        sys.stderr.write(("pterr,%s") % line)
        return

    # sourceid 提前校验
    try:
        lid = record["lid"]
        if str(lid) == "":
            sys.stderr.write(("liderr,%s") % line)
            return
        if lid not in Meizi_info.keys():
            sys.stderr.write(("liderr,%s") % line)
            return
    except KeyError:
        sys.stderr.write(("liderr,%s") % line)
        return

    # date, time
    try:
        timedata = time.strptime(timetmp, "%Y%m%d%H%M%S")
        timetmp_date, timetmp_time, timeStamp = formatTime(timedata)
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)
        return
    except KeyError:
        sys.stderr.write(("timeerr,%s") % line)
        return

    live_infos = Meizi_info[lid]
    isvalid, activityid, cameraid = CheckLiveTime(timeStamp, live_infos)

    if isvalid == -1:
        sys.stderr.write(("timeerr,%s") % line)
        return
    elif isvalid == -2:
        sys.stderr.write(("overtimerr,%s") % line)
        return


    # IP
    try:
        formatstring = formatstring + ',' + str(iptmp)
    except ValueError:
        sys.stderr.write(("iperr,%s") % line)
        return

    # location
    try:
        locationtmp = formatLocation(iptmp)
        location_province = locationtmp[2]
        location_city = locationtmp[3]
        formatstring = formatstring + ',' + str(location_province) + ',' + str(location_city)
    except ValueError:
        sys.stderr.write(("locationerr,%s") % line)
        return
    except TypeError:
        sys.stderr.write(("locationerr,%s") % line)
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
                sys.stderr.write(("platform, %s") % line)
                return
            formatstring = formatstring + ',' + clienttp
        except KeyError:
            sys.stderr.write(("platform, %s") % line)
            return

        # aver
        formatstring = formatstring + ','

        # liveid
        formatstring = formatstring + ',' + str(lid)

        # cameraid
        formatstring = formatstring + ',' + str(cameraid)
        # activityid
        formatstring = formatstring + ',' + str(activityid)
        print formatstring
    except ValueError:
        return

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    start_time = sys.argv[2]
    Meizi_info = LoadLiveMeizi(start_time)
    for line in fileinput.input(sys.argv[3:]):
        rt_live_pcweb_format(line)
