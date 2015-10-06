#!/bin/bash
. /etc/pydota.conf

topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")
work_path="${pydota_path}"
start_time=`date --date="$DATE + 1 hour" +%Y%m%d%H`
end_time=`date --date="$DATE + 2 hour" +%Y%m%d%H`
start_time=${start_time}"00"
end_time=${end_time}"00"

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
    filenameerr="err_"${start_time}"_play_"${topic}".log"
    filename=${start_time}"_play_"${topic}".bz2"
    python ./bin/kafka_connect.py $topic ${pydota_collect_pids} \
      | python ./bin/kafka_split.py ${start_time} ${end_time} ${topic} 2>${pydota_orig}/${sub_path}/$filenameerr \
      | bzip2 > ${pydota_orig}/${sub_path}/$filename &
    msg="${msg}${topic}:"
done
