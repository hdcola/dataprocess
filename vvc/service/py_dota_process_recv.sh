#!/bin/sh


# 日志收集的topic名称
#topics=(rt_live_pcweb mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012 mpp_vv_macclient_121_20151028 mpp_vv_win10client_511_20151030 mobile_live_2011_20151105 ott_live)
topics=(mpp_vv_msite)

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
fi

start_time=${start_time}"00"
work_path="/home/dota/pydota/pydota"
pydota_ott_live="/data/nfs/live_recv"

sub_year=${start_time:0:4}
sub_month=${start_time:4:2}
sub_day=${start_time:6:2}
sub_hour=${start_time:8:2}

# 存原始日志的本机目录,和logserver服务器文件名一样
recv_path="/home/dota/data/recv/"

mkdir -p ${recv_path}/${sub_year}/${sub_month}/ott_live 2>/dev/null

cd ${work_path}
ott_live_file=(`ls ${pydota_ott_live}/OTT_Live_recv_${start_time:0:10}*`)
if [ ${#ott_live_file[@]} -gt 1 ];then
    cat ${ott_live_file[*]} > ${recv_path}/${sub_year}/${sub_month}/ott_live/${start_time:0:10}"_ott_live_log"
    touch ${recv_path}/${sub_year}/${sub_month}/ott_live/".done_"${start_time}"_ott_live"
fi

for topic in ${topics[*]};
do
    local_file_path=${recv_path}/${sub_year}/${sub_month}/${topic}/

    if [ -f ${local_file_path}".done_"${start_time:0:10}"_"${topic} ];then
        ./service/py_dota_rawdata_recv.sh ${topic} ${start_time} &
    fi
done