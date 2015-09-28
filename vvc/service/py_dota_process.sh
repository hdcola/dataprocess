#!/bin/sh

. /etc/pydota.conf
topics=("mpp_vv_pcweb")
work_path="${pydota_path}"
start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
start_time=${start_time}"00"
cd $work_path
for topic in ${topics}; do
    filename=${start_time}"_"${topic}
    if [ -f ${pydota_orig}/${filename}.bz2 ]; then
      ./service/py_dota_count_vv.sh ${filename} $topic &
    fi
done
