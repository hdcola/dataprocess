#!/bin/sh
# 计算指定月的vv数据 以及制定某一天的汇总数据
# py_dota_report_vv_month.sh 201510
# py_dota_report_vv_month.sh 20151014

if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

start_time=$1
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"
cd $work_path

function report(){
  filename=day_vv_${start_time}*.csv
  files=`ls ${pydota_report}${sub_path}/${filename}`
  cat ${files} | awk -F, '{
    type=$1;
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum) {
        print sum[i]" "i
      }
    }' | awk '{print $2","$1}' | sort \
    > ${pydota_report}/${sub_path}/month_vv_${start_time}.csv

    #设置bearychat发送目标为dota-日报
    export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/1d2c96785da623e3299c1d742c4a26fb"

    msg=`cat ${pydota_report}/${sub_path}/month_vv_${start_time}.csv`
    nowtime=`date "+%Y/%m/%d %H:%M:%S"`
    msg="${msg}
    ${nowtime}@${py_dota_process_user}"
    echo "${msg}" | $bearychat -t "${start_time}的月VV数据统计完成"
}

report
