#!/bin/bash -x
filename=$1
topic=$2
work_path="/home/junjian/vvc"
cd $work_path
bzcat $filename.bz2 | python ${topic}_format.py ./geoip 2> err_${filename}.log | bzip2 > vv_${filename}.bz2
if [ -f vv_${filename}.bz2 ]; then
    python count_vv_5min.py ${topic} "all" vv_$filename.bz2 &
    python count_vv_5min.py ${topic} "chn" vv_$filename.bz2 &
    python count_vv_5min.py ${topic} "pl" vv_$filename.bz2 &

    python count_vv_hour.py ${topic} "all" vv_$filename.bz2 &
    python count_vv_hour.py ${topic} "chn" vv_$filename.bz2 &
    python count_vv_hour.py ${topic} "pl" vv_$filename.bz2 &
fi
