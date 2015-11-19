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

function report_vv(){
    sub_topic=$1
    topic_num=$2
    # 全天运行，逐小时合并各个topic数据
    echo "DATE,TIME,CID,PLID,VID,PT,LN,CLIENTTP,CLIENTVER,VV" >${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv
    rm ${pydota_report}/${sub_path}/.done_${start_time}_vv_${clienttype}_vid.csv
    for i in {0..23}
    do
        cur_time=`date --date="$start_time $i hour" +%Y%m%d%H`
        filename=${cur_time}*${sub_topic}*

        # 某一个小时时，只有所有相关topic的文件
        files=(`ls ${pydota_des}/${sub_path}/${filename}|grep -v "live"`)

        is_null=$?
        if [[ ${is_null} -ne 0 ]];then
            continue
        fi

        cat ${files[@]} | awk -F, -v clienttype=${clienttype} '{ if($21=="play" && $22==clienttype )
        {print $1","substr($2,1,2)","$11","$12","$13","$17","$18","$22","$23} }' \
        | sort | uniq -c | sort -rn |awk '{print $2","$1}' \
        >> ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv

        topmsg=`cat ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv|tail -n 10`
        report_size=`ls -lh ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv | awk '{print $5}'`

        msg="report_size大小${report_size}
        ${topmsg}"
        msg="${msg}
        @${py_dota_process_user}"
        #echo "${msg}" | $bearychat -t "${start_time} ${clienttype}的${i}点的数据统计完成"

    # for
    done
    touch ${pydota_report}/${sub_path}/.done_${start_time}_vv_${clienttype}_vid.csv
    sudo cp ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv ${pydota_nfs}/${sub_path}/${start_time}_vv_${clienttype}_vid.csv
    exit 0
}

if [ -n "$1" ]; then
  clienttype=$1
  if [ x"${clienttype}" == "xpcweb" ];then
    report_vv pcweb 1
  elif [ x"${clienttype}" == "xipad" ];then
    report_vv mobile 3
  elif [ x"${clienttype}" == "xapad" ];then
    report_vv mobile 3
  elif [ x"${clienttype}" == "xiphone" ];then
    report_vv mobile 3
  elif [ x"${clienttype}" == "xphonem" ];then
    report_vv msite 1
  elif [ x"${clienttype}" == "xandroid" ];then
    report_vv mobile 3
  elif [ x"${clienttype}" == "xott" ];then
    report_vv ott 4
  elif [ x"${clienttype}" == "xpcclient" ];then
    report_vv pcclient 1
  elif [ x"${clienttype}" == "xpadweb" ];then
    report_vv padweb 1
  elif [ x"${clienttype}" == "xwin10client" ];then
    report_vv win10client 1
  elif [ x"${clienttype}" == "xmacclient" ];then
    report_vv macclient 1
  else
    exit -1
  fi
else
  clienttype="phonem"
  report_vv msite 1
fi
