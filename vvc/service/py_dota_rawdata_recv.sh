#!/bin/sh

declare -A topic_file_prefix=([mpp_vv_pcweb]="printf access_%s-%s-%s-%s*" [mpp_vv_mobile]="printf mobile-vod_%s%s%s_%s*" \
[mpp_vv_mobile_new_version]="printf bid-2.0.1-default_%s%s%s_%s*" \
[mpp_vv_pcclient]="printf access_%s-%s-%s-%s*" \
[mpp_vv_msite]="printf access_%s-%s-%s-%s*" \
[mpp_vv_padweb]="printf bid-4.0.3-default_%s%s%s_%s*" \
[mpp_vv_ott]="printf llott-vod_%s%s%s_%s*" \
[ott_vv_41]="printf OTT-vod_%s%s%s_%s*" \
[ott_vv_44]="printf bid-3.0.1-default_%s%s%s_%s*" \
[mpp_vv_mobile_211_20151012]="printf bid-2.1.1-default_%s%s%s_%s*" \
[ott_vv_311_20151012]="printf bid-3.1.1-default_%s%s%s_%s*" \
[mpp_vv_macclient_121_20151028]="printf bid-1.2.1-default_%s%s%s_%s*" \
[mpp_vv_win10client_511_20151030]="printf bid-5.1.1-default_%s%s%s_%s*" \
[rt_live_pcweb]="printf bid-1.1.1.1-default_%s%s%s_%s_*" \
[mobile_live_2011_20151105]="printf bid-2.0.1.1-default_%s%s%s_%s*" \
[ott_live]="printf %s%s%s%s_ott_live_log" \
[mobile_pv]="printf bid-2.2.1-default_%s%s%s_%s*" \
[pcweb_pv]="printf bid-1.1.2-default_%s%s%s_%s*")


topic=$1
start_time=$2
sub_year=${start_time:0:4}
sub_month=${start_time:4:2}
sub_day=${start_time:6:2}
sub_hour=${start_time:8:2}
filename=`${topic_file_prefix[${topic}]} ${sub_year} ${sub_month} ${sub_day} ${sub_hour}`
work_path="/home/dota/pydota/pydota"

# 存原始日志的本机目录,和logserver服务器文件名一样
recv_path="/home/dota/data/recv/"

local_file_path=${recv_path}/${sub_year}/${sub_month}/${topic}/

cd ${work_path}

file=(`ls ${local_file_path}/${filename}`)
if [ ${#file[@]} -ge 1 ];then
    cat ${file[*]} | python format/format_${topic}.py ./geoip ${start_time} &
fi