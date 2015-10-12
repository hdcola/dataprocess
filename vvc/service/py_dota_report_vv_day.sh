#!/bin/sh
# 从全天的小时数据中计算日VV数据
# py_dota_report_vv_day.sh 201510072200 ott_vv_44
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
filename=${start_time}"_*"${field}".csv"
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path

cat ${pydota_report}${filename} | awk -F, '{
  type=$1","$2","$3;
  if(!(type in sum)){
    sum[type]=0};
    sum[type]=sum[type]+$NF
  }
  END{
    for(i in sum) {
      print sum[i]" "i
    }
  }'  | sort -rn | awk '{print $2","$1}'
