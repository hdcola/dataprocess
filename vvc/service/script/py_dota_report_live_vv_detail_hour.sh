#!/bin/sh
# 从raw数据中计算各个平台每个小时的数据
# py_dota_report_vv_detail_hour.sh pcweb 20151007

#设置bearychat发送目标为dota-日报
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/4dc6e829b29d810a677f67af1c1e945f"

if [ $# -eq 2 ];then
    start_time=$2
else
    start_time=`date +%Y%m%d`
fi

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}

work_path="/home/dota/pydota/pydota"
pydota_report="/home/dota/data/dailyreport"
pydota_des="/home/dota/data/des"
bearychat="${work_path}/bin/bearychat.sh"
pydota_nfs="/data/nfs/dota/"
py_dota_process_user="gibbsxu@10.100.1.141"

cd ${work_path}

function report_live_vv(){
    sub_topic=$1
    topic_num=$2
    # 全天运行，逐小时合并各个topic数据
    echo "DATE,TIME,PT,LN,CLIENTTP,CLIENTVER,SOURCEID,CAMERAID,ACTIVITYID,VV" >${pydota_report}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv
    rm ${pydota_report}/${sub_path}/.done_live_${start_time}_vv_${clienttype}_sourceid.csv
    for i in {0..23}
    do
        cur_time=`date --date="$start_time $i hour" +%Y%m%d%H`
        filename=${cur_time}*${sub_topic}*

        # 某一个小时时，只有所有相关topic的文件
        if [[ ${sub_topic} == "mobile" ]];then
            files=(`ls ${pydota_des}/${sub_path}/${cur_time}*mobile_live* ${pydota_des}/${sub_path}/${cur_time}*mobile_211_*`)
        else
            files=(`ls ${pydota_des}/${sub_path}/${filename}`)
        fi

        is_null=$?
        if [[ ${is_null} -ne 0 && ${#files[@]} -eq 0 ]];then
            continue
        fi

        cat ${files[@]} | awk -F, -v clienttype=${clienttype} '{ if($21=="play" && $22==clienttype && $17==4 )
        {print $1","substr($2,1,2)","$17","$18","$22","$23","$24","$25","$26} }' \
        | sort | uniq -c | sort -rn |awk '{print $2","$1}' \
        >> ${pydota_report}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv

        topmsg=`cat ${pydota_report}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv|tail -n 10`
        report_size=`ls -lh ${pydota_report}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv | awk '{print $5}'`

        msg="report_size大小${report_size}
        ${topmsg}"
        msg="${msg}
        @${py_dota_process_user}"
        #echo "${msg}" | $bearychat -t "${start_time} ${clienttype}的${i}点的数据统计完成"

    # for
    done
    touch ${pydota_report}/${sub_path}/.done_live_${start_time}_vv_${clienttype}_sourceid.csv
    sudo cp ${pydota_report}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv ${pydota_nfs}/${sub_path}/live_${start_time}_vv_${clienttype}_sourceid.csv
    exit 0
}

if [ -n "$1" ]; then
  clienttype=$1
  if [ x"${clienttype}" == "xpcweb" ];then
    report_live_vv live_pcweb 1
  elif [ x"${clienttype}" == "xipad" ];then
    report_live_vv mpp_vv_mobile_211_20151012 1
  elif [ x"${clienttype}" == "xiphone" ];then
    report_live_vv mobile 2
  elif [ x"${clienttype}" == "xandroid" ];then
    report_live_vv mobile 2
  elif [ x"${clienttype}" == "xott" ];then
    report_live_vv ott_live 1
  elif [ x"${clienttype}" == "xpcclient" ];then
    report_live_vv live_pcweb 1
  else
    exit -1
  fi
else
  clienttype="phonem"
  report_live_vv msite 1
fi
