#!/bin/sh

. /etc/pydota.conf
topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb")
work_path="${pydota_path}"
start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
start_time=${start_time}"00"

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path=${sub_path_year}/${sub_path_month}
mkdir -p ${pydota_log} 2>/dev/null
mkdir -p ${pydota_pid_path} 2>/dev/null
mkdir -p ${pydota_orig}/${sub_path} 2>/dev/null
mkdir -p ${pydota_des}/${sub_path} 2>/dev/null
mkdir -p ${pydota_report}/${sub_path} 2>/dev/null
cd $work_path
for topic in ${topics}; do
    filename=${start_time}"_"${topic}
    if [ -f ${pydota_orig}/${sub_path}/${filename}.bz2 ]; then
      ./service/py_dota_count_vv.sh ${filename} $topic $sub_path_year $sub_path_month &
    fi
done
