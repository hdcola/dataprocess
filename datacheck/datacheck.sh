#!/bin/bash
#$1 is time
#$2 is topic list such as: mpp_vv_pcweb, mpp_vv_mobile, mpp_vv_mobile_new_version, mpp_vv_pcclient, mpp_vv_msite, mpp_vv_padweb, mpp_vv_ott, ott_vv_41, ott_vv_44
#!
if [ "$1" ]; then
	atime="$1"
else
	atime=$(date +%Y%m%d%H)
fi
atime=2015100812

junjian_path_orig="/home/junjian/pydota/orig/"
junjian_path_des="/home/junjian/pydota/des/"
datareport_path="/home/guangdong/datacheck/report/"
#原始 report 路径
#junjian_path_report="/home/junjian/pydota/report/"

#重新计算 report 路径
junjian_path_report="/home/junjian/pydota/re-report/"
ayear="${atime:0:4}"
amonth="${atime:4:2}"
#ben_path_orig="/data/matrix/"
#ben_path_des=""
ben_path_report="/data/matrix/result/"
adate="${atime:0:8}"
#echo ${junjian_path_report}
#根据流判断 ben 的数据路径

#echo "${atime}" "${amonth}" "${adate}"

topics=("mpp_vv_pcweb" "mpp_vv_mobile" "mpp_vv_mobile_new_version" "mpp_vv_pcclient" "mpp_vv_msite" "mpp_vv_padweb" "mpp_vv_ott" "ott_vv_41" "ott_vv_44")
ben_path=("pcp" "mobile_old" "mobile" "pcc" "mz" "padweb" "ott" "ott41" "ott44")

#for topic in ${topics}; do
#	if [ "$2" == "${topic}" ]; then


#test chage
#获取 topics 的长度
len_topics=${#topics[@]}

#将各端 report 进行对比
for ((i=0; i<${len_topics}; i++)); do

	echo "日期,军建时间,军建VV,ben时间,benVV,相差千分比,差值" > ${datareport_path}${topics[$i]}.${adate}.csv
	#paste "${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv" "${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv" > /home/guangdong/datacheck/report/${topics[$i]}.${adate}.test1.csv
	 paste "${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv" "${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv" | awk 'BEGIN {FS=","} {printf "%s,%s,%s\n", $1, $2, $4}' | \
	 #计算
	 awk 'BEGIN {FS=" "} {if ($3!="") {printf "%s,%s,%s\n", $1, substr($2,length($2)-5,2), $3} else {printf "%s,%s\n", $1, $2}}' | \
	 awk 'BEGIN {FS=","} { if ($3!="" && $5!="") {printf "%s,%s,%s,%s,%s,%s‰,%s\n", $1, $2, $3, $4, $5, substr(($3-$5)/$5*1000, 0, 5), ($3-$5)} \
   else if (length($1)<10) {printf "%s,%s,%s,null,null,null,null\n", $1, $2, $3 } \
   else {printf "null,null,null,%s,%s,null,null\n", substr($1,length($1)-5,2), $2}}' >> ${datareport_path}${topics[$i]}.${adate}.csv
done
