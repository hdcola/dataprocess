#!/bin/sh
# py_dota_process.sh 直接处理上小时的数据
# py_dota_process.sh 201510072300 处理指定时间的数据

if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

topics=(mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012)
#topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44")
topics_tmp=`echo ${topics[*]}`

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
      return $_xrsh_cnt
    fi
    _xrsh_cnt=$(( $_xrsh_cnt + 1 ))
  done
  return "-1"
}

cd $work_path

# 当没有done文件时，等待，有done时，执行，且从topics数组中unset
while true
do
    len=${#topics[@]}
    if [ ${len} -eq 0 ];then
        break
    fi

    for topic in ${topics[*]};
    do
        done_filename="done_"${start_time}_${topic}
        if [ -f ${pydota_orig}/${sub_path}/${done_filename} ]; then
            ./service/py_dota_rawdata.sh $topic $start_time &
            xrsh_arritemidx "$topics_tmp" "$topic"
            i=$?
            unset topics[$i]
        fi

#            msg="${msg}./service/py_dota_rawdata.sh $topic $start_time &"
    done

done
#for topic in ${topics}; do
#    filename=${start_time}"_play_"${topic}
#    done_filename="done_"${start_time}_${topic}
#    if [ -f ${pydota_orig}/${sub_path}/${done_filename} ]; then
#      ./service/py_dota_rawdata.sh $topic $start_time &
#
#      msg="${msg}./service/py_dota_rawdata.sh $topic $start_time &
#
#"
#    fi
#done

# 详细处理数据报送
# echo "${msg}" | $bearychat -t "py_dota_process开始处理${start_time}数据"
# 简洁处理数据报送
echo "${topics_tmp}" | $bearychat -t "py_dota_process开始处理${start_time}数据"
