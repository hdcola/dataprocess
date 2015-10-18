#!/bin/sh
#按魔方客户端分类出对比结果
if [ "$1" ]; then
  atime=$1
else
  atime=$(date, %Y%m%d)
fi
#文件目录
file_path="/Users/guangdong/Documents/mgtv/datacheckreport"

clienttype=("mpp_vv_pcweb" "mpp_vv_mobile" "mpp_vv_mobile_new_version" "mpp_vv_mobile_211_20151012" "mpp_vv_pcclient" "mpp_vv_msite" "mpp_vv_padweb" "mpp_vv_ott" "ott_vv_41" "ott_vv_44" "ott_vv_311_20151012")
len_clienttype="${#clienttype[@]}"

for ((i=0; i<${len_clienttype}; i++)); do
  #文件名称
  file_ben="${file_path}/topic_ben_${atime}_${clienttype[$i]}.csv"
  file_guodong="${file_path}/topic_guodong_${atime}_${clienttype[$i]}.csv"
  file_report="${file_path}/report_topic_${atime}_${clienttype[$i]}.csv"
  # sed '/^$/d' ${file_guodong} ${file_ben}
  # echo "${file_guodong}" "${file_ben}"
  echo "time,guodong,ben,dif,difratio(milli),client" > ${file_report}
  paste -d',' ${file_guodong} ${file_ben} | awk -F',' '{if (NR>1) print $1","$2","$5","($2-$5)","($2-$5)/$5*1000","$6}' >> ${file_report}
done
