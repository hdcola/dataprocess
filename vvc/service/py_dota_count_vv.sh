#!/bin/sh

. /etc/pydota.conf
filename=$1
topic=$2
work_path="${pydota_path}"
cd $work_path
bzcat ${pydota_orig}/$filename.bz2 | python bin/format/${topic}_format.py ./geoip 2> ${pydota_des}/err_${filename}.log | bzip2 > ${pydota_des}/vv_${filename}.bz2
if [ -f ${pydota_des}/vv_${filename}.bz2 ]; then
    python bin/count_vv_5min.py ${topic} "all" ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_5min.py ${topic} "chn" ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_5min.py ${topic} "pl"  ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "all" ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "chn" ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "pl"  ${pydota_des}/vv_$filename.bz2 ${pydota_report} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
fi
