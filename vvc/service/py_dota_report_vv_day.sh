#!/bin/sh
# 计算指定天的vv数据
# py_dota_report_vv_day.sh 20151007
# 使用指定维度计算指定天的vv数据
# py_dota_report_vv_day.sh 2015100722 cid


if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

start_time=$1
field=$2
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"
cd $work_path

function report(){
  filename=${start_time}*${field}.csv
  files=`ls ${pydota_report}${sub_path}/${filename}`
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
    > ${pydota_report}/${sub_path}/day_vv_${start_time}.csv
}

if [ -n "$2" ]; then
  field=$2
  report
else
  field="cid"
  report
fi
