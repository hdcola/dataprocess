#!/bin/sh

. /etc/pydota.conf
filename=$1
topic=$2
sub_path_year=$3
sub_path_month=$4
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
cd $work_path
bzcat ${pydota_orig}/${sub_path}/$filename.bz2 | python bin/format/format_${topic}.py ./geoip \
  2> ${pydota_des}/${sub_path}/err_${filename}.log | bzip2 > ${pydota_des}/${sub_path}/vv_${filename}.bz2

if [ -f ${pydota_des}/${sub_path}/vv_${filename}.bz2 ]; then
    python bin/count_vv_5min.py ${topic} "all" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_5min.py ${topic} "chn" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_5min.py ${topic} "pl"  ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "all" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "chn" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "pl"  ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
fi
