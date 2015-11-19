#!/bin/sh
# 从raw数据中计算各个平台一天总VV数据
# py_dota_report_total.sh 20151007

#设置bearychat发送目标为dota-日报
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/5a3d3583ecb52af13590a801bab94aa9"

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date -d yesterday +%Y%m%d`
fi
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path_hour=${start_time:8:2}


sub_path=${sub_path_year}/${sub_path_month}
work_path="/home/dota/pydota/pydota"
pydota_des="/home/dota/data/des"
pydota_report="/home/dota/data/dailyreport"

mkdir -p ${pydota_report}/${sub_path} 2>/dev/null

cd $work_path

function report_vv_total(){

    filenameraw=${start_time}*

    files=`ls ${pydota_des}/${sub_path}/${filenameraw}  | grep -v "live"`
    #files=`ls ${pydota_des}/${sub_path}/${filenameraw} ${pydota_des}/${sub_path_nextday}/${filenamenext}`

    cat ${files} | awk -F, '{
    if($21=="play" && $17==0){
      print $1","substr($2,1,2)","$22}
    }' | sort | uniq -c | awk '{print $2","$1}' | sort -n \
    > ${pydota_report}/${sub_path}/day_vv_hour_${start_time}.csv

    cat ${pydota_report}/${sub_path}/day_vv_hour_${start_time}.csv | awk -F, '{
    type=$1","$3;
    if(!(type in sum)){
      sum[type]=0};
      sum[type]=sum[type]+$NF
    }
    END{
      for(i in sum){
        print sum[i]" "i
      }
    }'|awk '{print $2","$1}'>${pydota_report}/${sub_path}/day_vv_total_${start_time}.csv

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
}
report_vv_total