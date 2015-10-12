#!/bin/sh
# 手工指定处理指定类型指定时间的数据 比如2015101020
# py_dota_count_vv.sh topic start_time
# 自动处理指定类型两小时之前的处理
# py_dota_count_vv.sh topic

if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

[ "$#" == "0" ] && echo "usage: py_dota_reprocess.sh  [topic] [start_time] " && exit 1

if [ $# -ge 2 ];then
  start_time=$2;
else
  start_time=`date --date="$DATE - 2 hour" +%Y%m%d%H`
  start_time=${start_time}"00"
fi

#start_time=${1:-${start_time}}
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}

topic=$1
filename=${start_time}"_play_"${topic}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path
filenameraw=${start_time}"_playrawdata_"${topic}


if [ -f ${pydota_des}/${sub_path}/${filenameraw}.bz2 ]; then
    #python bin/count_vv_5min.py ${topic} "all" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    #python bin/count_vv_5min.py ${topic} "chn" ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    #python bin/count_vv_5min.py ${topic} "pl"  ${pydota_des}/${sub_path}/vv_$filename.bz2 ${pydota_report}/${sub_path} &
    #[ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "all" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "chn" ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}

    python bin/count_vv_hour.py ${topic} "pl"  ${pydota_des}/${sub_path}/$filenameraw.bz2 ${pydota_report}/${sub_path} &
    [ ! -z ${pydota_process_pids} ] && echo $! >> ${pydota_process_pids}
fi