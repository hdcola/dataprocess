#!/bin/sh
# py_dota_process.sh 直接处理上小时的数据
# py_dota_process.sh 201510072300 处理指定时间的数据

if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")
work_path="${pydota_path}"
start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
start_time=${start_time}"00"
start_time=${1:-${start_time}}

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path=${sub_path_year}/${sub_path_month}
bearychat="${work_path}/bin/bearychat.sh"
mkdir -p ${pydota_log} 2>/dev/null
mkdir -p ${pydota_pid_path} 2>/dev/null
mkdir -p ${pydota_orig}/${sub_path} 2>/dev/null
mkdir -p ${pydota_des}/${sub_path} 2>/dev/null
mkdir -p ${pydota_report}/${sub_path} 2>/dev/null
msg=""

cd $work_path
for topic in ${topics}; do
    filename=${start_time}"_play_"${topic}
    if [ -f ${pydota_orig}/${sub_path}/${filename}.bz2 ]; then
      ./service/py_dota_count_vv.sh $topic $sub_path_year $sub_path_month $start_time &

      msg="${msg}./service/py_dota_count_vv.sh $topic $sub_path_year $sub_path_month $start_time &

"
    fi
done

echo "${msg}" | $bearychat -t "py_dota_process开始处理${start_time}数据"
