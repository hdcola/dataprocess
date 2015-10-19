#!/bin/bash
if [ "$1" ]; then
  atime=$1
else
  atime=$(date +%Y%m%d)
fi

#取出年份和月份
ayear=${atime:0:4}
amonth=${atime:4:2}

#rawdata 路径 pydota_path_des路径与本老师不同
pydota_path_des="/home/fengbenming/data/des/${ayear}/${amonth}"
checkreport_path="/home/guangdong/datacheck/report"

#整点数组
aclock=("00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23")

#整点数组长度
len_aclock=${#aclock[@]}

#定义各 topic 通配符
mpp_vv_pcweb="_playrawdata_mpp_vv_pcweb*"
mpp_vv_mobile="_playrawdata_mpp_vv_mobile"
mpp_vv_mobile_new_version="_playrawdata_mpp_vv_mobile_new_version*"
mpp_vv_mobile_211_20151012="_playrawdata_mpp_vv_mobile_211_20151012*"
mpp_vv_pcclient="_playrawdata_mpp_vv_pcclient*"
mpp_vv_msite="_playrawdata_mpp_vv_msite*"
mpp_vv_padweb="_playrawdata_mpp_vv_padweb*"
mpp_vv_ott="_playrawdata_mpp_vv_ott*"
ott_vv_41="_playrawdata_ott_vv_41*"
ott_vv_44="_playrawdata_ott_vv_44*"
ott_vv_311_20151012="_playrawdata_ott_vv_311_20151012*"

topics=("mpp_vv_pcweb" "mpp_vv_mobile" "mpp_vv_mobile_new_version" "mpp_vv_mobile_211_20151012" "mpp_vv_pcclient" "mpp_vv_msite" "mpp_vv_padweb" "mpp_vv_ott" "ott_vv_41" "ott_vv_44" "ott_vv_311_20151012")
#定义 clienttype

len_topics="${#topics[@]}"
#新建 report 文件, 覆盖原有文件
for ((i=0; i<${len_topics}; i++)); do
  rawfile="${topics[$i]}"
  report_client=${rawfile}
  reportfile="${checkreport_path}/topic_ben_${atime}_${report_client}.csv"
  echo "" > ${reportfile}
done

function count_vv_pertopic() {
  for ((j=0; j<${len_topics}; j++)); do
  {
    rawfile_dict_key="${topics[$j]}"
    rawfile="${rawfile_dict[${rawfile_dict_key}]}"
    report_client=${rawfile_dict_key}
    reportfile="${checkreport_path}/topic_ben_${atime}_${report_client}.csv"
    if  [ ${rawfile_dict_key} = "mpp_vv_ott" ] || [ ${rawfile_dict_key} = "ott_vv_41" ] || [ ${rawfile_dict_key} = "ott_vv_44" ] || [ ${rawfile_dict_key} = "ott_vv_311_20151012" ] ; then
      cat ${rawfile} | awk -F',' '{if ($7!="-" && $7!="") print $7 }' | wc -l | awk '{printf "%s,%s,%s\n", ahour, $1, clienttype}' ahour="${ahour}" clienttype=${report_client} >> ${reportfile}
    else
      cat ${rawfile} | wc -l | awk '{printf "%s,%s,%s\n", ahour, $1, clienttype}' ahour="${ahour}" clienttype=${report_client} >> ${reportfile}
    fi
  }&
  done
}

#遍历全天24小时各端 rawdata 并输出结果到 report
for ((i=0; i<${len_aclock}; i++)); do
  #定义当前小时
  ahour="${atime}${aclock[$i]}00"

  declare -A rawfile_dict=([mpp_vv_pcweb]="${pydota_path_des}/${ahour}${mpp_vv_pcweb}" [mpp_vv_mobile]="${pydota_path_des}/${ahour}${mpp_vv_mobile}" [mpp_vv_mobile_new_version]="${pydota_path_des}/${ahour}${mpp_vv_mobile_new_version}" [mpp_vv_mobile_211_20151012]="${pydota_path_des}/${ahour}${mpp_vv_mobile_211_20151012}" [mpp_vv_pcclient]="${pydota_path_des}/${ahour}${mpp_vv_pcclient}" [mpp_vv_msite]="${pydota_path_des}/${ahour}${mpp_vv_msite}" [mpp_vv_padweb]="${pydota_path_des}/${ahour}${mpp_vv_padweb}"  [mpp_vv_ott]="${pydota_path_des}/${ahour}${mpp_vv_ott}" [ott_vv_41]="${pydota_path_des}/${ahour}${ott_vv_41}" [ott_vv_44]="${pydota_path_des}/${ahour}${ott_vv_44}" [ott_vv_311_20151012]="${pydota_path_des}/${ahour}${ott_vv_311_20151012}")
  count_vv_pertopic
  wait

done
