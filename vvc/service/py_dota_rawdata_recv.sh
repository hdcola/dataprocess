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
[pcweb_pv]="printf bid-1.1.2-default_%s%s%s_%s*" \
[macclient_vv_811_20151210]="printf bid-8.1.1-default_%s%s%s_%s*")


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
des_path="/home/dota/data/des/"
md5_check_path="/home/dota/data/md5_check/"
mkdir -p ${md5_check_path}/${sub_year}/${sub_month}/ 2>/dev/null

local_file_path=${recv_path}/${sub_year}/${sub_month}/${topic}/

cd ${work_path}

file=(`ls ${local_file_path}/${filename}`)
if [ ${#file[@]} -ge 1 ];then
    cat ${file[*]} | python format/format_${topic}.py ./geoip ${start_time}

    desfiles=(`ls ${des_path}/*/*/*rawdata_${topic}_${start_time}`)

    if [ ${#desfiles[@]} -ge 1 ];then
        for des_file in ${desfiles[*]};
        do
            tmp_file_name=`basename ${des_file}`
            if [[ ${topic} == "mpp_vv_mobile_211_20151012" ]];then
                cat ${des_file} |awk -F, '{if($17==0 || $17==3){print $0}}'| python service/made_md5.py > ${md5_check_path}/${sub_year}/${sub_month}/${tmp_file_name}.md5
                # 生成mobile_211中的直播md5文件
                len=${#tmp_file_name}
                cat ${des_file} |awk -F, '{if($17==4){print $0}}'| python service/made_md5.py > ${md5_check_path}/${sub_year}/${sub_month}/${tmp_file_name:0:${len}-12}live_${tmp_file_name:${len}-12}.md5
                touch ${md5_check_path}/${sub_year}/${sub_month}/.done_${topic}_live_${start_time}.md5
            else
                cat ${des_file} | python service/made_md5.py > ${md5_check_path}/${sub_year}/${sub_month}/${tmp_file_name}.md5
            fi
        done

    fi
    touch ${md5_check_path}/${sub_year}/${sub_month}/.done_${topic}_${start_time}.md5

    exit 0
else
    touch ${md5_check_path}/${sub_year}/${sub_month}/.done_${topic}_${start_time}.md5
fi