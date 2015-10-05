#!/bin/sh

. /etc/pydota_reprocess.conf
[ "$#" != "1" ] && echo "usage: py_dota_reprocess.sh  [length/hour] " && exit 1

count=$1
n=0
while [ $count -ge $n ]; do
    hour=$((count-n))
    topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")
    work_path="${pydota_path}"
    start_time=`date --date="$DATE - $hour hour" +%Y%m%d%H`
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
    for topic in ${topics}; do
        filename=${start_time}"_play_"${topic}
        if [ -f ${pydota_orig}/${sub_path}/${filename}.bz2 ]; then
          ./service/py_dota_count_vv_re.sh ${filename} $topic $sub_path_year $sub_path_month $start_time &
        fi
    done
    n=$((n+1))
done
