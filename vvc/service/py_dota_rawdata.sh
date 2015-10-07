#!/bin/sh
# 从原始数据加工清理出rawdata数据用于最终的数据计算
# py_dota_count_vv.sh ott_vv_44 201510072200
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

topic=$1
start_time=$2
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
filename=${start_time}"_play_"${topic}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path
filenameraw=${start_time}"_playrawdata_"${topic}

bzcat ${pydota_orig}/${sub_path}/$filename.bz2 | python format/format_${topic}.py ./geoip \
  2> ${pydota_des}/${sub_path}/err_${filenameraw}.log | bzip2 > ${pydota_des}/${sub_path}/${filenameraw}.bz2

err_count=`cat ${pydota_des}/${sub_path}/err_${filenameraw}.log | wc -l`
raw_size=`ls -l ${pydota_des}/${sub_path}/${filenameraw}.bz2 | awk '{print $5}'`
msg="error数据有${err_count}条,raw数据有${raw_size}"
echo "${msg}" | $bearychat -t "${topic} ${start_time}的rawdata数据处理完成"
