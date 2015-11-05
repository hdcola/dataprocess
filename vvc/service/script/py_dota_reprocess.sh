#!/bin/sh
# 移动端数据较大，各个时间段并行运行，其他端并行运行。
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota_reprocess.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/pydota_reprocess"
fi

#. /etc/pydota_reprocess.conf
[ "$#" != "4" ] && echo "usage: py_dota_reprocess.sh  [date] [start_hour] [end_hour] " && exit 1

#topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")
datetime=$1
start_hour=$2
end_hour=$3
topic=$4
date -d $datetime +%Y%m%d 1>/dev/null 2>&1 || exit 1
while [ $end_hour -ge $start_hour ]; do
    work_path="${pydota_path}"
    start_time=`date --date="$datetime $start_hour hour" +%Y%m%d%H`
    start_time=${start_time}"00"
    sub_path_year=${start_time:0:4}
    sub_path_month=${start_time:4:2}
    sub_path=${sub_path_year}/${sub_path_month}
    mkdir -p ${pydota_log} 2>/dev/null
    mkdir -p ${pydota_pid_path} 2>/dev/null
    mkdir -p ${pydota_orig}/${sub_path} 2>/dev/null
    mkdir -p ${pydota_des}/${sub_path} 2>/dev/null
    mkdir -p ${pydota_report}/${sub_path} 2>/dev/null
    cd $work_path
    filename=${start_time}"_play_"${topic}
    if [ -f ${pydota_orig}/${sub_path}/${filename} ]; then
        # 仅mobile端后台运行，并行
        if [[ ${topic} =~ "mobile" ]];then
            ./service/script/py_dota_count_vv_re.sh ${filename} $topic $sub_path_year $sub_path_month $start_time 2>${pydota_log}/${start_time}_${topic} &
        else
            ./service/script/py_dota_count_vv_re.sh ${filename} $topic $sub_path_year $sub_path_month $start_time 2>${pydota_log}/${start_time}_${topic}
        fi
    fi
    start_hour=$((start_hour+1))
done
