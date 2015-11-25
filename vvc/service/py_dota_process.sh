#!/bin/sh


# 日志收集的topic名称
topics=(mobile_pv pcweb_pv)
#topics=(mpp_vv_msite)
topics_tmp=`echo ${topics[*]}`

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
fi

start_time=${start_time}"00"
work_path="/home/dota/pydota/pydota"
pydota_ott_live="/data/nfs/live_recv"

sub_year=${start_time:0:4}
sub_month=${start_time:4:2}
sub_day=${start_time:6:2}
sub_hour=${start_time:8:2}

# 存原始日志的本机目录,和logserver服务器文件名一样
recv_path="/home/dota/data/recv/"

#获取数组中给定元素的下标
#参数：1 数组; 2 元素
#返回：元素在数组中的下标，从 0 开始；-1 表示未找到
#例子：
#    获取数组 xrsh_array 中元素 i3 的下标
#    xrsh_array=(i1 i2 i3)
#    xrsh_tmp=`echo ${xrsh_array[*]}`
#    xrsh_arritemidx "$xrsh_tmp" "i3"
#    返回 2
#注意：数组作为参数使用时需要先转换
function xrsh_arritemidx()
{
  local _xrsh_tmp
  local _xrsh_cnt=0
  local _xrsh_array=`echo "$1"`
  for _xrsh_tmp in ${_xrsh_array[*]}; do
    if test "$2" = "$_xrsh_tmp"; then
      return ${_xrsh_cnt}
    fi
    _xrsh_cnt=$(( $_xrsh_cnt + 1 ))
  done
  return -1
}

cd ${work_path}

while true
do
    len=${#topics[@]}
    if [ ${len} -eq 0 ];then
        break
    fi

    for topic in ${topics[*]};
    do
        local_file_path=${recv_path}/${sub_year}/${sub_month}/${topic}/

        if [ -f ${local_file_path}".done_"${start_time:0:10}"_"${topic} ];then
            ./service/py_dota_rawdata_recv.sh ${topic} ${start_time} &
            xrsh_arritemidx "$topics_tmp" "$topic"
            i=$?
            if [ ${i} -ge 0 ]; then
                unset topics[${i}]
            fi
        fi
    done
done
