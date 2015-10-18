#!/bin/sh
#按魔方客户端分类出对比结果
if [ "$1" ]; then
  atime=$1
else
  atime=$(date, %Y%m%d)
fi
#文件目录
file_path="/Users/guangdong/Documents/mgtv/datacheckreport"

clienttype=("mobile" "msite" "ott" "padweb" "pcclient" "pcweb")
len_clienttype="${#clienttype[@]}"

for ((i=0; i<${len_clienttype}; i++)); do
  #文件名称
  file_ben="${file_path}/ben_${atime}_${clienttype[$i]}.csv"
  file_guodong="${file_path}/guodong_${atime}_${clienttype[$i]}.csv"
  file_report="${file_path}/report_${atime}_${clienttype[$i]}.csv"
  # sed '/^$/d' ${file_guodong} ${file_ben}
  # echo "${file_guodong}" "${file_ben}"
  echo "time,guodong,ben,dif,difratio(milli),client" > ${file_report}
  paste -d',' ${file_guodong} ${file_ben} | awk -F',' '{print $1","$2","$5","($2-$5)","($2-$5)/$5*1000","$6}' >> ${file_report}
done
