#!/bin/sh

. /etc/pydota.conf
. $pydota_service/py_dota.common

filename=$1
topic=$2
sub_path_year=$3
sub_path_month=$4
start_time=$5
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"

cd $work_path
filenameraw=${start_time}"_playrawdata_"${topic}

srcno=`bzcat ${pydota_orig}/${sub_path}/$filename.bz2 | wc -l`
bearchat_send "${0}开始${filenameraw}处理，${pydota_orig}/${sub_path}/$filename.bz2有${srcno}条记录"

bzcat ${pydota_orig}/${sub_path}/$filename.bz2 | python format/format_${topic}.py ./geoip \
  2> ${pydota_des}/${sub_path}/err_${filenameraw}.log | bzip2 > ${pydota_des}/${sub_path}/${filenameraw}.bz2

errno=`cat ${pydota_des}/${sub_path}/err_${filenameraw}.log| wc -l`
srcno=`bzcat ${pydota_des}/${sub_path}/${filenameraw}.bz2 | wc -l`
bearchat_send "${0}处理${filenameraw}完毕，${pydota_des}/${sub_path}/err_${filenameraw}.log:$errno，${pydota_des}/${sub_path}/${filenameraw}.bz2:${srcno}"

if [ -f ${pydota_des}/${sub_path}/${filenameraw}.bz2 ]; then
    #python bin/count_vv_5min.py ${topic} "all" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    #python bin/count_vv_5min.py ${topic} "chn" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    #python bin/count_vv_5min.py ${topic} "pl"  ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "all" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    bearchat_send "count_vv_hour处理all的${pydota_des}/${sub_path}/$filenameraw.bz2完毕"

    python bin/count_vv_hour.py ${topic} "chn" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    bearchat_send "count_vv_hour处理chn的${pydota_des}/${sub_path}/$filenameraw.bz2完毕"

    python bin/count_vv_hour.py ${topic} "pl"  ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    bearchat_send "count_vv_hour处理pl的${pydota_des}/${sub_path}/$filenameraw.bz2完毕"
fi
