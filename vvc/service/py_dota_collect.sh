#!/bin/bash
topics=("mpp_vv_pcweb")
work_path="/home/junjian/vvc/"
start_time=`date --date="$DATE + 1 hour" +%Y%m%d%H`
end_time=`date --date="$DATE + 2 hour" +%Y%m%d%H`
start_time=${start_time}"00"
end_time=${end_time}"00"
cd $work_path
for topic in ${topics}; do
    filename=${start_time}"_"${topic}".bz2"
    python kafka_connect.py $topic | python kafka_split.py ${start_time} ${end_time} 2>/dev/null | bzip2 > $filename &
done