#!/bin/sh
# 从raw数据中计算VV数据
# py_dota_report_vv.sh 201510072200 ott_vv_44
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

#设置bearychat发送目标为dota-处理结果
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/4dc6e829b29d810a677f67af1c1e945f"

start_time=$1
topic=$2
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
filename=${start_time}"_play_"${topic}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path
filenameraw=${start_time}"_playrawdata_"${topic}
filenamereport=${start_time}"_"${topic}

function report(){
  #计算指定字段和字段名的report
  # report field_no field_name
  # report 11 cid
  field_no=$1
  field_name=$2
  proctime=`date "+%Y/%m/%d %H:%M:%S"`
  bzcat ${pydota_des}/${sub_path}/${filenameraw}.bz2 \
    | awk -F"," -v field_no="${field_no}" '{ if($21=="play") {print $1","substr($2,1,2)","$field_no","$22","$23} }' \
    | sort | uniq -c | sort -rn | awk '{print $2","$1}' \
    > ${pydota_report}/${sub_path}/${filenamereport}_${field_name}.csv

  csv_count=`cat ${pydota_report}/${sub_path}/${filenamereport}_${field_name}.csv | wc -l`
  topmsg=`cat ${pydota_report}/${sub_path}/${filenamereport}_${field_name}.csv | head -5`

  msg="${field_name}数据有${csv_count}条
  ${topmsg}"
  nowtime=`date "+%Y/%m/%d %H:%M:%S"`
  msg="${msg}
  ${proctime}-${nowtime}@${py_dota_process_user}"
  echo "${msg}" | $bearychat -t "${topic} ${start_time:0:8} ${start_time:8:2}:${start_time:10:2}的${field_name}数据统计完成"
}

report 11 "cid"
report 12 "plid"
report 13 "vid"
