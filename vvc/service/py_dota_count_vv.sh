#!/bin/sh
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

topic=$1
sub_path_year=$2
sub_path_month=$3
start_time=$4
filename=${start_time}"_play_"${topic}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"

cd $work_path
filenameraw=${start_time}"_playrawdata_"${topic}

#bzcat ${pydota_orig}/${sub_path}/$filename.bz2 | python format/format_${topic}.py ./geoip \
#  2> ${pydota_des}/${sub_path}/err_${filenameraw}.log | bzip2 > ${pydota_des}/${sub_path}/${filenameraw}.bz2

# if [ -f ${pydota_des}/${sub_path}/${filenameraw}.bz2 ]; then
#     #python bin/count_vv_5min.py ${topic} "all" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
#     #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
#
#     #python bin/count_vv_5min.py ${topic} "chn" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
#     #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
#
#     #python bin/count_vv_5min.py ${topic} "pl"  ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
#     #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
#
#     python bin/count_vv_hour.py ${topic} "all" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
#     [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
#
#     python bin/count_vv_hour.py ${topic} "chn" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
#     [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
#
#     python bin/count_vv_hour.py ${topic} "pl"  ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
#     [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
# fi
