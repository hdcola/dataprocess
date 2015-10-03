#!/usr/bin/env python
# encoding: utf-8

import fileinput
import sys
import time
import string
import urllib
import json
from IPy import IP

filesfps = []
filesfpscount = 0
GEOIP_SORT = []
GEOIP  = {}

def loadGeoIp(filename):
    fp  = open(filename)
    for i, line in enumerate(fp):
        try:
            record = string.split(line, "\t")
            rangmin  = record[0]
            rangmax  = record[1]
            country  = record[2]
            province = record[3]
            city     = record[4]
            operator = record[6]
            rangmin = IP(rangmin).int()
            rangmax = IP(rangmax).int()
            GEOIP[rangmin] = [rangmax, country, province, city, operator]
            GEOIP_SORT.append(rangmin)
        except ValueError:
            sys.stderr.write(("value error,%s") % line)
    GEOIP_SORT.sort()
    fp.close()

def getRangeKey(userip):
    low = 0
    height = len(GEOIP_SORT)-1
    while low < height:
        mid = (low+height)/2
        if GEOIP_SORT[mid] < userip and GEOIP_SORT[mid + 1] < userip:
            low = mid + 1
        elif GEOIP_SORT[mid] > userip and GEOIP_SORT[mid - 1] > userip:
            height = mid - 1
        elif GEOIP_SORT[mid] <= userip and GEOIP_SORT[mid +1] > userip:
            return GEOIP_SORT[mid]
        elif GEOIP_SORT[mid -1] <= userip and GEOIP_SORT[mid] > userip:
            return GEOIP_SORT[mid -1]
        elif GEOIP_SORT[mid + 1] == userip:
            return GEOIP_SORT[mid +1]
        else:
            return None
    return None

def formatLocation(userip):
    userip = userip.strip('""')
    userip = IP(userip).int()
    location = getRangeKey(userip)
    if location and GEOIP[location]:
        if location <= userip <= GEOIP[location][0]:
            return GEOIP[location]
    else:
        return None

def formatTime(timetmp):
    try:
        timedata = time.localtime(timetmp)
    except ValueError:
        raise ValueError("timeerr")
    timetmp_date = time.strftime('%Y%m%d', timedata)
    timetmp_time = time.strftime('%H%M%S', timedata)
    return timetmp_date, timetmp_time

def collectArgs(fstring, argslist, name, errname, strict):
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
        sys.stderr.write(("%s,%s") % (errname, line))
        raise ValueError("args is illegal")
        return

def ott_41_format(line):
    formatstring = ""
    if len(line.strip('\n')) == 0:
        return
    try:
        record = json.loads(line)
    except ValueError:
        sys.stderr.write(("jsonerr,%s") % line)
        return

    # date, time
    try:
        timetmp = float(record['time'])
        timetmp_date, timetmp_time = formatTime(timetmp)
        formatstring = str(timetmp_date) + ',' + str(timetmp_time)
    except ValueError:
        sys.stderr.write(("timeerr,%s") % line)
        return
    except KeyError:
        sys.stderr.write(("timeerr,%s") % line)
        return

    # IP
    try:
        iptmp = record["ip"].strip()
        formatstring = formatstring + ',' + str(iptmp)
    except KeyError:
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

    try:
        # uid
        formatstring = collectArgs(formatstring, record, "user_id", "user_iderr", False)
        # uuid
        formatstring = collectArgs(formatstring, record, "play_session", "play_sessionerr", True)
        # guid
        formatstring = formatstring + ','
        # ref
        formatstring = formatstring + ','
        # bid
        formatstring = formatstring + ','
        # cid
        try:
            cid = record["video_info"]['fstlvl_id']
            formatstring = formatstring + ',' + str(cid)
        except KeyError:
            sys.stderr.write(("video_info.fstlvl_iderr,%s") % line)
            return
        # plid
        try:
            plid = record["video_info"]['sndlv_id']
            if plid.strip() == "":
                sys.stderr.write(("video_info.sndlv_iderr,%s") % line)
                return
            else:
                formatstring = formatstring + ',' + str(plid)
        except KeyError:
            sys.stderr.write(("video_info.sndlv_iderr,%s") % line)
            return
        # vid
        try:
            vid = record["video_info"]['clip_id']
            if vid.strip() == "":
                sys.stderr.write(("video_info.clip_iderr,%s") % line)
                return
            else:
                formatstring = formatstring + ',' + str(vid)
        except KeyError:
            sys.stderr.write(("video_info.clip_iderr,%s") % line)
            return
        # tid
        formatstring = formatstring + ','
        # vts
        formatstring = formatstring + ','
        # cookie
        formatstring = collectArgs(formatstring, record, "mac", "macerr", True)
        # pt
        formatstring = formatstring + ',' + '0'
        # ln
        formatstring = formatstring + ','
        # cf
        formatstring = formatstring + ','
        # definition
        try:
            definition = record["video_info"]['definition']
            if definition.strip() == "":
                sys.stderr.write(("video_info.definitionerr,%s") % line)
                return
            else:
                formatstring = formatstring + ',' + str(definition)
        except KeyError:
            sys.stderr.write(("video_info.definitionerr,%s") % line)
            return

        # act
        formatstring = formatstring + ','
        # CLIENTTP
        formatstring = formatstring + ',' + "ott"
        # aver
        formatstring = collectArgs(formatstring, record, "apk_version", "apk_versionerr", True)
        print formatstring
    except ValueError:
        return
    # vid
    #try:
    #    vid = record["video_info"]['video_id']
    #    formatstring = formatstring + ',' + str(vid)
    #except KeyError:
    #    vid = ""
    #    formatstring = formatstring + ',' + str(vid)

    ## definition
    #try:
    #    definition = record['video_info']['definition']
    #    formatstring = formatstring + ',' + str(definition)
    #except KeyError:
    #    definition = ""
    #    formatstring = formatstring + ',' + str(definition)

if __name__ == '__main__':
    # gzcat abc.gz | python pcp_format.py ./genip -
    # python pcp_format.py ./genip afile bfile cfile
    loadGeoIp(sys.argv[1])
    for line in fileinput.input(sys.argv[2:]):
        ott_41_format(line)
