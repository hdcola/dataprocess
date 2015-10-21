#!/bin/sh
# 从raw数据中计算VV数据
# py_dota_report_vv_day_1021.sh 20151019
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

#设置bearychat发送目标为dota-处理结果
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/5a3d3583ecb52af13590a801bab94aa9"

start_time=$1
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

filename=*${start_time}*vv.csv

proctime=`date "+%Y/%m/%d %H:%M:%S"`
rm ${pydota_report}${sub_path}/${filename}

./bin/py_dota_report.py -t ${start_time} -d ${pydota_report}/${sub_path} ${pydota_des}/${sub_path}/${start_time}*

files=`ls ${pydota_report}${sub_path}/${filename}`

for file in ${files};do
    topmsg=`cat ${file}`
    report_size=`ls -lh ${file} | awk '{print $5}'`
    file_name=`basename ${file}`

    msg="report_size大小${report_size}
${topmsg}"
nowtime=`date "+%Y/%m/%d %H:%M:%S"`
msg="${msg}
${proctime}-${nowtime}@${py_dota_process_user}"
echo "${msg}" | $bearychat -t "${file_name}的数据统计完成"


done
