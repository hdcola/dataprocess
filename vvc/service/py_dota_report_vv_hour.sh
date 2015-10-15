#!/bin/sh
# 计算指定小时的vv指定维度数据
# py_dota_report_vv_hour.sh 2015101322 cid
# 计算指定小时的vv所有维度数据
# py_dota_report_vv_hour.sh 2015101322


if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

function print_help()
{
    echo "usage: py_dota_report_vv_hour.sh [start_time] [field] [clienttype]"
    echo "--start_time: 计算数据的日期，精确到小时"
    echo "--field: 媒资内容的纬度, 值为vid/cid/plid，为空时计算全部"
    echo "--clienttype: 终端类型，值为pcweb/pcclient/mobile/padweb/msite/ott/mpp，为空时为全平台"
    echo "samples:"
    echo "-----------------------------------------------------------------------------------"
    echo "py_dota_report_vv_hour.sh 2015101322    vid    mpp   : mpp指定小时的vid vv数据"
    echo "py_dota_report_vv_hour.sh 2015101322    cid          : 全端指定小时的cid vv数据"
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
    type=$1","$2","$3;
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum) {
        print sum[i]" "i
      }
    }' | awk '{print $2","$1}' | sort \
    > ${pydota_report}/${sub_path}/hour_vv_${field}_${start_time}_${clienttype}.csv
}

if [ -n "$2" ]; then
  field=$2
  report
else
  field="plid"
  report
  field="vid"
  report
  field="cid"
  report
fi
