#!/bin/sh
# 计算指定天的vv数据
# py_dota_report_vv_day.sh 20151007
# 使用指定维度计算指定天的vv数据
# py_dota_report_vv_day.sh 20151007 cid


if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

function print_help()
{
    echo "usage: py_dota_report_vv_day_new.sh [start_time] [field] [clienttype]"
    echo "--start_time: 计算数据的日期，精确到日"
    echo "--field: 媒资内容的纬度, 值为vid/cid/plid"
    echo "--clienttype: 终端类型，值为pcweb/pcclient/mobile/padweb/msite/ott/mpp，为空时为全平台"
    echo "samples:"
    echo "-----------------------------------------------------------------------------------"
    echo "py_dota_report_vv_day_new.sh 20151013    vid    mpp   : mpp指定日期各个小时的vid vv数据"
    echo "py_dota_report_vv_day_new.sh 20151013    cid          : 所有端指定日期各个小时的cid vv数据"
    echo "-----------------------------------------------------------------------------------"
}


if [ $# -ge 1 ];then
    start_time=$1
else
    print_help
    exit 1
fi

if [ -n "$3" ]; then
  clienttype=$3
else
  clienttype=""
fi

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"
cd $work_path


function report(){
  filename=${start_time}*${clienttype}*${field}.csv
  if [ "${clienttype}" == "mpp" ];then
    files=`ls ${pydota_report}${sub_path}/${filename}|grep -v "ott"`
  else
    files=`ls ${pydota_report}${sub_path}/${filename}`
  fi

  if [ a"${clienttype}" == "a" ];then
    clienttype="all"
  fi

  cat ${files} | awk -F, '{
    if($3==""){
      type=$1",NULL";
    }else{
      type=$1","$3;
    }
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum) {
        print sum[i]" "i
      }
    }' | awk '{print $2","$1}' | sort \
    > ${pydota_report}/${sub_path}/day_vv_${field}_${start_time}_${clienttype}.csv

    #设置bearychat发送目标为dota-日报
    export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/1d2c96785da623e3299c1d742c4a26fb"

    msg=`cat ${pydota_report}/${sub_path}/day_vv_${field}_${start_time}_${clienttype}.csv|sort -t"," -k3rn | head -n 10`
    report_size=`ls -lh ${pydota_report}/${sub_path}/day_vv_${field}_${start_time}_${clienttype}.csv | awk '{print $5}'`
    nowtime=`date "+%Y/%m/%d %H:%M:%S"`
    msg="report_size的大小${report_size}
    ${msg}
    ${nowtime}@${py_dota_process_user}"
    echo "${msg}" | $bearychat -t "${start_time}的${clienttype}的${field}日VV数据统计完成"
}

if [ -n "$2" ]; then
  field=$2
  report
else
  field="cid"
  report
fi
