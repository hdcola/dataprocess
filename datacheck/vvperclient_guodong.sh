#!/bin/bash
if [ "$1" ]; then
  atime=$1
else
  atime=$(date +%Y%m%d)
fi

#取出年份和月份
ayear=${atime:0:4}
amonth=${atime:4:2}

#rawdata 路径
pydota_path_des="/home/xuguodong/pydota/des/${ayear}/${amonth}"
checkreport_path="/home/guangdong/datacheck/report"

#整点数组
aclock=("00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23")

#整点数组长度
len_aclock=${#aclock[@]}

#定义各端通配符
mobile="_playrawdata_mpp_vv_mobile*"
ott="_playrawdata_mpp_vv_ott*"
ott_1="_playrawdata_ott_vv*"
msite="_playrawdata_mpp_vv_msite*"
padweb="_playrawdata_mpp_vv_padweb*"
pcweb="_playrawdata_mpp_vv_pcweb*"
pcclient="_playrawdata_mpp_vv_pcclient*"

#定义 clienttype
clienttype=("rawdata_mobile" "rawdata_ott" "rawdata_msite" "rawdata_padweb" "rawdata_pcweb" "rawdata_pcclient")

len_clienttype="${#clienttype[@]}"

#新建 report 文件, 覆盖原有文件
for ((i=0; i<${len_clienttype}; i++)); do
  rawfile="${clienttype[$i]}"
  report_client=${rawfile#*_}
  reportfile="${checkreport_path}/guodong_${atime}_${report_client}.csv"
  echo "" > ${reportfile}
done

#计算 VV 函数, 调用该函数会遍历单小时各端的 rawdata, 并将结果输出到 report 文件
function count_vv() {
  for ((j=0; j<${len_clienttype}; j++)); do
  {
    rawfile_dict_key="${clienttype[$j]}"
    rawfile="${rawfile_dict[${rawfile_dict_key}]}"
    report_client=${rawfile_dict_key#*_}
    reportfile="${checkreport_path}/guodong_${atime}_${report_client}.csv"
    cat ${rawfile} | wc -l | awk '{printf "%s,%s,%s\n", ahour, $1, clienttype}' ahour="${ahour}" clienttype=${report_client} >> ${reportfile}
    #echo ${rawfile}
  }&
  done
}

#遍历全天24小时各端 rawdata 并输出结果到 report
for ((i=0; i<${len_aclock}; i++)); do
  #定义当前小时
  ahour="${atime}${aclock[$i]}00"

  declare -A rawfile_dict=([rawdata_mobile]="${pydota_path_des}/${ahour}${mobile}" [rawdata_ott]="${pydota_path_des}/${ahour}${ott} ${pydota_path_des}/${ahour}${ott_1} " [rawdata_msite]="${pydota_path_des}/${ahour}${msite}" [rawdata_padweb]="${pydota_path_des}/${ahour}${padweb}" [rawdata_pcweb]="${pydota_path_des}/${ahour}${pcweb}" [rawdata_pcclient]="${pydota_path_des}/${ahour}${pcclient}")

  count_vv
  wait

done
