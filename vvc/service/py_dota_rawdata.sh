#!/bin/sh
# 从原始数据加工清理出rawdata数据用于最终的数据计算
# py_dota_count_vv.sh ott_vv_44 201510072200

topic=$1
start_time=$2
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path_hour=${start_time:8:2}
filename=recv_${sub_path_year}"_"${sub_path_month}"_"${sub_path_day}"_"${sub_path_hour}"_"${topic}"_log"
sub_path=${sub_path_year}/${sub_path_month}
work_path="/home/xuguodong/pydota/pydota"

pydota_orig="/home/xuguodong/data/recv"
pydota_des="/home/xuguodong/data/des"

cd $work_path
filenameraw=des_${start_time}"_"${topic}

cat ${pydota_orig}/${filename} | python format/format_${topic}.py ./geoip ${start_time} &
