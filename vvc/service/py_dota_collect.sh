#!/bin/bash
# 从kafka中将对应的信息收集下来
# 启动后，自动计算时间，从下一小时开始处理，由于kafka上的时间延迟，所以建议提前至少10分钟启动
# 本程序可以使用cron来启动

if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012")
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

# 计算开始、结束时间，已小时为单位，时间格式共12位
start_time=`date --date="$DATE + 1 hour" +%Y%m%d%H`
end_time=`date --date="$DATE + 2 hour" +%Y%m%d%H`
start_time=${start_time}"00"
end_time=${end_time}"00"

# 获得子目录
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path=${sub_path_year}/${sub_path_month}

# 建立相关目录
mkdir -p ${pydota_log} 2>/dev/null
mkdir -p ${pydota_pid_path} 2>/dev/null
mkdir -p ${pydota_orig}/${sub_path} 2>/dev/null
mkdir -p ${pydota_des}/${sub_path} 2>/dev/null
mkdir -p ${pydota_report}/${sub_path} 2>/dev/null

# 回到工程目录
cd $work_path

msg=""

# 接受目标kafka topic数据，合要求的数据压缩落地，非法数据写入对应错误日志
for topic in ${topics}; do
    filenameerr="err_"${start_time}"_play_"${topic}".log"
    filename=${start_time}"_play_"${topic}".bz2"
    # 后台运行，结束时间半小时后，进程退出
    ./bin/kafka_connect.py ${topic} ${pydota_collect_pids} \
      | ./bin/kafka_split.py ${start_time} ${end_time} ${topic} ${pydota_orig}/${sub_path} 2>${pydota_orig}/${sub_path}/$filenameerr \
      | bzip2 > ${pydota_orig}/${sub_path}/$filename &

    msg="${msg}./bin/kafka_connect.py ${topic} ${pydota_collect_pids} | ./bin/kafka_split.py ${start_time} ${end_time} ${topic} 2>${pydota_orig}/${sub_path}/$filenameerr | bzip2 > ${pydota_orig}/${sub_path}/$filename

"
done

# 详细处理数据报送
# echo "${msg}" | $bearychat -t "py_dota_collect开始处理${start_time}-${end_time}数据"
# 简洁处理数据报送
echo "${topics}" | $bearychat -t "py_dota_collect开始处理${start_time}-${end_time}数据"
