#!/bin/sh
# 计算指定天的各个端每个小时的总vv数据
# py_dota_report_vv_day.sh 20151007 vid
# 使用指定维度计算指定天的vv数据
# py_dota_report_vv_day.sh 20151007  cid pcweb

function print_help()
{
    echo "计算各个平台一天内每个小时的总vv"
    echo "usage: py_dota_report_vv_day.sh [start_time] [clienttype]"
    echo "--start_time: 计算数据的日期，精确到日"
    echo "--clienttype: 终端类型，值为pcweb/pcclient/mobile/padweb/msite/ott/mpp，为空时为全平台"
    echo "samples:"
    echo "-----------------------------------------------------------------------------------"
    echo "py_dota_report_vv_day.sh 20151013   vid  mpp   : mpp指定天从vid纬度的各个小时的总vv"
    echo "py_dota_report_vv_day.sh 20151013          : 所有平台从cid纬度同指定天的各个小时的总vv"
    echo "-----------------------------------------------------------------------------------"
}


if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi


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
    type=$1","$2;
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum) {
        print sum[i]" "i
      }
    }' | awk '{print $2","$1}' | sort \
    > ${pydota_report}/${sub_path}/total_day_vv_${field}_${start_time}_${clienttype}.csv

    #设置bearychat发送目标为dota-日报
    export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/1d2c96785da623e3299c1d742c4a26fb"

    msg=`cat ${pydota_report}/${sub_path}/total_day_vv_${field}_${start_time}_${clienttype}.csv`
    nowtime=`date "+%Y/%m/%d %H:%M:%S"`
    msg="${msg}
    ${nowtime}@${py_dota_process_user}"
    echo "${msg}" | $bearychat -t "${start_time}的${clienttype}的${field}的日分时VV数据统计完成"
}

if [ -n "$2" ]; then
  field=$2
  report
else
  field="cid"
  report
fi
