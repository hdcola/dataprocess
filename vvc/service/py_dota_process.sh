#!/bin/sh
# py_dota_process.sh 直接处理上小时的数据
# py_dota_process.sh 2015100723 处理指定时间的数据

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date --date="$DATE - 1 hour" +%Y%m%d%H`
fi

topics=(mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012 mpp_vv_macclient_121_20151028 mpp_vv_win10client_511_20151030 rt_live_pcweb mobile_live_2011_20151105 ott_live)
#topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")

start_time=${start_time}"00"

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path_hour=${start_time:8:2}

sub_path=${sub_path_year}/${sub_path_month}
work_path="/home/xuguodong/pydota/pydota"

pydota_orig="/home/xuguodong/data/recv"
pydota_ott_live="/data/nfs/live_recv"

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
#function xrsh_arritemidx()
#{
#  local _xrsh_tmp
#  local _xrsh_cnt=0
#  local _xrsh_array=`echo "$1"`
#  for _xrsh_tmp in ${_xrsh_array[*]}; do
#    if test "$2" = "$_xrsh_tmp"; then
#      return $_xrsh_cnt
#    fi
#    _xrsh_cnt=$(( $_xrsh_cnt + 1 ))
#  done
#  return "-1"
#}

cd $work_path

# 收集ott_live日志
ott_live_file=(`ls ${pydota_ott_live}/OTT_Live_recv_${start_time:0:10}*`)
if [ ${#ott_live_file[@]} -gt 1 ];then
    cat ${ott_live_file[*]} > ${pydota_orig}/recv_${sub_path_year}"_"${sub_path_month}"_"${sub_path_day}"_"${sub_path_hour}"_ott_live_log"
fi

for topic in ${topics[*]};
do
  filename=recv_${sub_path_year}"_"${sub_path_month}"_"${sub_path_day}"_"${sub_path_hour}"_"${topic}"_log"
  if [ -f ${pydota_orig}/${filename} ]; then
    ./service/py_dota_rawdata.sh $topic $start_time &
  fi
done

# 当没有done文件时，等待，有done时，执行，且从topics数组中unset
#while true
#do
#    len=${#topics[@]}
#    if [ ${len} -eq 0 ];then
#        break
#    fi
#
#    for topic in ${topics[*]};
#    do
#        done_filename=".done_"${start_time}_${topic}
#        if [ -f ${pydota_orig}/${sub_path}/${done_filename} ]; then
#            ./service/py_dota_rawdata.sh $topic $start_time &
#            xrsh_arritemidx "$topics_tmp" "$topic"
#            i=$?
#            unset topics[$i]
#        fi
#
##            msg="${msg}./service/py_dota_rawdata.sh $topic $start_time &"
#    done
#
#done

#echo "${topics_tmp}" | $bearychat -t "py_dota_process开始处理${start_time}数据"
