#!/bin/sh
# 从raw数据中计算一天VV数据
# py_dota_report_day_gibbs.sh 20151007 ott_vv_44
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

#设置bearychat发送目标为dota-日报
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/5a3d3583ecb52af13590a801bab94aa9"

start_time=$1
topic=$2
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path

function report_vv_total(){
    proctime=`date "+%Y/%m/%d %H:%M:%S"`

    filenameraw=${start_time}*"_playrawdata_"*.bz2

    files=`ls ${pydota_des}${sub_path}/${filenameraw}`

    bzcat ${files} | awk -F, '{
    if($21=="play"){
      print $1","$22}
    }' | sort | uniq -c | sort -rn |awk '{print $2","$1}'\
    > ${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv

    cat ${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv | awk -F, '{
    type=$1",总计";
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum) {
        print sum[i]" "i
      }
    }'|awk '{print $2","$1}'>>${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv

    sed -i '1i\日期,平台,vv'  ${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv

    topmsg=`cat ${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv`
    report_size=`ls -lh ${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv | awk '{print $5}'`

    msg="report_size大小${report_size}
${topmsg}"
nowtime=`date "+%Y/%m/%d %H:%M:%S"`
msg="${msg}
${proctime}-${nowtime}@${py_dota_process_user}"
echo "${msg}" | $bearychat -t "${start_time}的各个端总vv"

}
report_vv_total