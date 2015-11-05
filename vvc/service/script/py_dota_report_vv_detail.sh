#!/bin/sh
# 从raw数据中计算各个平台每个小时的数据
# py_dota_report_day_gibbs.sh 20151007
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi


if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date -d yesterday +%Y%m%d`
fi

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}

mkdir -p ${pydota_dailyreport}/${sub_path} 2>/dev/null
chmod -R 775 ${pydota_dailyreport} 2>/dev/null

work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path

./service/script/py_dota_report_vv_detail_hour.sh pcweb ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh ipad ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh apad ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh iphone ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh phonem ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh android ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh ott ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh pcclient ${start_time} &
./service/script/py_dota_report_vv_detail_hour.sh padweb ${start_time} &

./service/script/py_dota_report_vv_detail_plid_cid.sh ${start_time} &
