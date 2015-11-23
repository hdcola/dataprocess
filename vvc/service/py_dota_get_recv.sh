#!/bin/sh
# py_dota_process.sh 直接处理上小时的数据
# py_dota_process.sh 201510072300 处理指定时间的数据
#
#if [[ -e "/etc/pydota.conf" ]]; then
#  . /etc/pydota.conf
#fi
#
#if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
#  . "$HOME/.pydota"
#fi
#
if [[ -n "$HOME" && -e "$HOME/.pydota_topic" ]]; then
  . "$HOME/.pydota_topic"
fi
#. ./etc/pydota_topic.conf

# 日志收集服务器的文件目录数组。key：topic
declare -A topic_path=([mpp_vv_pcweb]="${mpp_vv_pcweb}" [mpp_vv_mobile]="${mpp_vv_mobile}" \
[mpp_vv_mobile_new_version]="${mpp_vv_mobile_new_version}" \
[mpp_vv_pcclient]="${mpp_vv_pcclient}" \
[mpp_vv_msite]="${mpp_vv_msite}" \
[mpp_vv_padweb]="${mpp_vv_padweb}" \
[mpp_vv_ott]="${mpp_vv_ott}" \
[ott_vv_41]="${ott_vv_41}" \
[ott_vv_44]="${ott_vv_44}" \
[mpp_vv_mobile_211_20151012]="${mpp_vv_mobile_211_20151012}" \
[ott_vv_311_20151012]="${ott_vv_311_20151012}" \
[mpp_vv_macclient_121_20151028]="${mpp_vv_macclient_121_20151028}" \
[mpp_vv_win10client_511_20151030]="${mpp_vv_win10client_511_20151030}" \
[rt_live_pcweb]="${rt_live_pcweb}" \
[mobile_live_2011_20151105]="${mobile_live_2011_20151105}")

# 不同topic的文件名称格式
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
[mobile_live_2011_20151105]="printf bid-2.0.1.1-default_%s%s%s_%s*")


# 日志收集的topic名称
topics=("rt_live_pcweb mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012 mpp_vv_macclient_121_20151028 mpp_vv_win10client_511_20151030 mobile_live_2011_20151105")
#topics=("mpp_vv_msite")

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
fi

sub_year=${start_time:0:4}
sub_month=${start_time:4:2}
sub_day=${start_time:6:2}
sub_hour=${start_time:8:2}

# 存在日志的本机目录
recv_path="/home/dota/data/recv/"
md5_path="/home/dota/data/md5sum_dir/"

for topic in ${topics};do
    mkdir -p ${recv_path}/${sub_year}/${sub_month}/${topic} 2>/dev/null
    mkdir -p ${md5_path}/${sub_year}/${sub_month}/${topic} 2>/dev/null
done

function md5_check(){
    logserver_md5_file=$1
    locacl_md5_file=$2
    err_md5_check=$3
    cat ${logserver_md5_file} ${locacl_md5_file} | sort | uniq -c | awk '{if($1!=2) print $0}' > ${err_md5_check}
    failed_num=`wc -l ${err_md5_check}|awk '{print $1}'`
    return ${failed_num}
}


for topic in ${topics};do
    if [[ ${topic} == "rt_live_pcweb" ]];then
        log_hosts=${log_aws_hosts}
    else
        log_hosts=${log_yg_hosts}
    fi

    flag_scp_topic=0

    # 远程日志服务器上面的文件名称
    filename=`${topic_file_prefix[${topic}]} ${sub_year} ${sub_month} ${sub_day} ${sub_hour}`
    src=${topic_path[${topic}]}"/"${filename}

    # 本地服务器文件名称
    local_file_path=${recv_path}/${sub_year}/${sub_month}/${topic}/

    # logserver文件md5值存入的文件名
    logserver_md5_file=${md5_path}/${sub_year}/${sub_month}/${topic}/${start_time}"_logserver_md5"

    # 接收文件的md5值存入文件名
    local_md5_file=${md5_path}/${sub_year}/${sub_month}/${topic}/${start_time}"_local_md5"

    rm ${logserver_md5_file} 2>/dev/null

    for IP in ${log_hosts};do
        # 远程ls，检测文件是否存在。防止数据量小时，某些机器无数据文件，干扰后续
        errmsg=`ssh "dota@"${IP} "cd ${topic_path[${topic}]} && ls ${filename}" 2>&1 `
        isexist=$?

        if [[ ${isexist} -eq 0 ]];then
            # 远程scp指定ip文件到本地
            scp "dota@"${IP}":"${src} ${recv_path}/${sub_year}/${sub_month}/${topic}/

            scp_errno=$?
            # scp失败后，报警通知
            if [ ${scp_errno} -ne 0 ];then
                flag_scp_topic=1
                err_msg_scp="${start_time}:${IP}:${topic} scp文件失败
                错误码:${scp_errno}"
                proxychains curl -X POST --data-urlencode "payload={\"text\":\"${err_msg_scp}\"}" https://hook.bearychat.com/=bw7by/incoming/71a4dcf2093e6b443a8b8f33d48fdac8
            fi
        elif [[ ${isexist} -eq 2 ]];then
            continue
        else
            err_msg="${start_time}:${IP}:${topic}
            错误信息:${errmsg}
            错误码:${isexist}"
            proxychains curl -X POST --data-urlencode "payload={\"text\":\"${err_msg}\"}" https://hook.bearychat.com/=bw7by/incoming/71a4dcf2093e6b443a8b8f33d48fdac8

            continue
        fi

        # 远程计算对应文件的md5值
        ssh "dota@"${IP} "cd ${topic_path[${topic}]} && md5sum ${filename}" |awk -v ip=${IP} '{print $0"_"ip}'>> ${logserver_md5_file}

        files=`ls ${local_file_path}/${filename}|grep 'log$\|COMPLETED$'`

        for file in ${files};do
            mv ${file} ${file}_${IP}
        done
    done

    err_md5_check=${md5_path}/${sub_year}/${sub_month}/${topic}/"err_"${start_time}"_md5_check"

    # 计算一个topic收集所有文件的md5值
    cd ${local_file_path} && md5sum ${filename} > ${local_md5_file}

    # 校验md5,返回错误文件数
    md5_check ${logserver_md5_file} ${local_md5_file} ${err_md5_check}
    errno=$?
    if [[ ${errno} -ge 1 ]];then
        err_msg=`cat ${err_md5_check}`
        err_msg="${start_time}:${topic}的md5校验失败
        ${err_msg}"
        proxychains curl -X POST --data-urlencode "payload={\"text\":\"${err_msg}\"}" https://hook.bearychat.com/=bw7by/incoming/71a4dcf2093e6b443a8b8f33d48fdac8
    elif [[ ${flag_scp_topic} -eq 1 ]];then
        continue
    else
        # 校验md5成功后，生成.done文件
        touch ${local_file_path}".done_"${start_time}"_"${topic}
    fi
done

