#!/bin/bash
#$1 is time
#$2 is topic list such as: mpp_vv_pcweb, mpp_vv_mobile, mpp_vv_mobile_new_version, mpp_vv_pcclient, mpp_vv_msite, mpp_vv_padweb, mpp_vv_ott, ott_vv_41, ott_vv_44
#!
if [ "$1" ]; then
	atime="$1"
else
	atime=$(date +%Y%m%d%H)
fi
#atime=2015100912
ayear="${atime:0:4}"
amonth="${atime:4:2}"
adate="${atime:0:8}"

#数据对比结果输出路径
datareport_path="/home/guangdong/datacheck/report/"

#军建 path
junjian_path_orig="/home/junjian/pydota/orig/"
junjian_path_des="/home/junjian/pydota/des/"
junjian_path_err="${junjian_path_des}${ayear}/${amonth}/"

#军建原始 report 路径
#junjian_path_report="/home/junjian/pydota/report/"

#军建重新计算 report 路径
junjian_path_report="/home/junjian/pydota/re-report/"

ben_path_data="/data/matrix/"
ben_path_report="${ben_path_data}result/"

topics=("mpp_vv_pcweb" "mpp_vv_mobile" "mpp_vv_mobile_new_version" "mpp_vv_pcclient" "mpp_vv_msite" "mpp_vv_padweb" "mpp_vv_ott" "ott_vv_41" "ott_vv_44")

ben_path=("pcp" "mobile_old" "mobile" "pcc" "mz" "padweb" "ott" "ott41" "ott44")

aclock=("00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23")

#获取 topics 的长度
len_topics=${#topics[@]}

#将各端 report 进行对比
for ((i=0; i<${len_topics}; i++)); do

     #军建和 ben 老师的report文件
	   junjian_file_report="${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv"
	   ben_file_report="${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv"


     #创建当日数据对比文件
	   echo "日期,军建时间,军建VV,ben时间,benVV,相差千分比,差值" > ${datareport_path}${topics[$i]}.${adate}.csv
	   #paste "${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv"   "${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv" > /home/guangdong/datacheck/report/${topics[$i]}.${adate}.test1.csv
	   paste "${junjian_file_report}"   "${ben_file_report}" | awk 'BEGIN {FS=","} {printf "%s,%s,%s\n", $1, $2, $4}' | \
	   #计算
	   awk 'BEGIN {FS=" "} {if ($3!="") {printf "%s,%s,%s\n", $1, substr($2,length($2)-5,2), $3} else {printf "%s,%s\n", $1, $2}}' | \
	   awk 'BEGIN {FS=","} { if ($3!="" && $5!="") {printf "%s,%s,%s,%s,%s,%s‰,%s\n", $1, $2, $3, $4, $5, substr(($3-$5)/$5*1000, 0, 5), ($3-$5)} \
     else if (length($1)<10) {printf "%s,%s,%s,null,null,null,null\n", $1, $2, $3 } \
     else {printf "null,null,null,%s,%s,null,null\n", substr($1,length($1)-5,2), $2}}' >> ${datareport_path}${topics[$i]}.${adate}.csv

		#  #创建当日原始数据和错误日志对比文件
		#  checkreport="${datareport_path}err_${topics[$i]}.${adate}.log"
		#  echo "${adate}_${topics[$i]} 数据对比结果" > ${checkreport}
		 #
		#  #遍历各个小时错误日志并进行统计, 写入当日错误报告文件
	  #  for ((j=0; j<24; j++)); do
		 #
    #     #军建和 ben 老师的原始数据文件
		# 		#junjian_file_orig="${junjian_path_des}${ayear}/${amonth}/${adate}${aclock[$j]}00_play_${topics[$i]}.bz2"
		# 		#ben_file_orig=""
		 #
		# 		#军建和 ben 老师的错误文件
		# 		junjian_file_err="${junjian_path_err}err_${adate}${aclock[$j]}00_playrawdata_${topics[$i]}.log"
		# 		ben_file_err="${ben_path_data}${ben_path}/exception/${adate}${aclock[$j]}_exception.csv"
		 #
		# 		#写入小时信息
	  #     echo "${adate}:${aclock[$j]}" >> ${checkreport}
		# 		echo " " >> ${checkreport}
		# 		echo "junjian_err:" >> ${checkreport}
		 #
		# 		#将军建 err 统计写入errreport
		# 		cat ${junjian_file_err} | awk 'BEGIN {FS=","} {printf "%s\n", $1}' | sort | uniq -c >> ${checkreport}
		 #
		# 		#军建错误和 ben 老师错误分割线
		# 		echo "-------------------------" >> ${checkreport}
		# 		echo "ben_err:" >> ${checkreport}
		 #
		# 		#ben 老师 err 统计写入 errreport
		# 		cat ${ben_file_err} | awk 'BEGIN {FS="|"} {printf "%s\n", $1}' | sort | uniq -c >> ${checkreport}
		 #
	  #     #小时分割线
		# 		echo "*************NEXT HOUR**************" >> ${checkreport}
		#  done

done

for ((i=0; i<${len_topics}; i++)); do

    #  #军建和 ben 老师的report文件
	  #  junjian_file_report="${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv"
	  #  ben_file_report="${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv"
		 #
		 #
    #  #创建当日数据对比文件
	  #  echo "日期,军建时间,军建VV,ben时间,benVV,相差千分比,差值" > ${datareport_path}${topics[$i]}.${adate}.csv
	  #  #paste "${junjian_path_report}${ayear}/${amonth}/${topics[$i]}_${adate}_vv_all_hour.csv"   "${ben_path_report}${ben_path[$i]}.${adate}.hour.vv.csv" > /home/guangdong/datacheck/report/${topics[$i]}.${adate}.test1.csv
	  #  paste "${junjian_file_report}"   "${ben_file_report}" | awk 'BEGIN {FS=","} {printf "%s,%s,%s\n", $1, $2, $4}' | \
	  #  #计算
	  #  awk 'BEGIN {FS=" "} {if ($3!="") {printf "%s,%s,%s\n", $1, substr($2,length($2)-5,2), $3} else {printf "%s,%s\n", $1, $2}}' | \
	  #  awk 'BEGIN {FS=","} { if ($3!="" && $5!="") {printf "%s,%s,%s,%s,%s,%s‰,%s\n", $1, $2, $3, $4, $5, substr(($3-$5)/$5*1000, 0, 5), ($3-$5)} \
    #  else if (length($1)<10) {printf "%s,%s,%s,null,null,null,null\n", $1, $2, $3 } \
    #  else {printf "null,null,null,%s,%s,null,null\n", substr($1,length($1)-5,2), $2}}' >> ${datareport_path}${topics[$i]}.${adate}.csv

		 #创建当日原始数据和错误日志对比文件
		 checkreport="${datareport_path}err_${topics[$i]}.${adate}.log"
		 echo "${adate}_${topics[$i]} 数据对比结果" > ${checkreport}

		 #遍历各个小时错误日志并进行统计, 写入当日错误报告文件
	   for ((j=0; j<24; j++)); do

        #军建和 ben 老师的原始数据文件
				#junjian_file_orig="${junjian_path_des}${ayear}/${amonth}/${adate}${aclock[$j]}00_play_${topics[$i]}.bz2"
				#ben_file_orig=""

				#军建和 ben 老师的错误文件
				junjian_file_err="${junjian_path_err}err_${adate}${aclock[$j]}00_playrawdata_${topics[$i]}.log"
				ben_file_err="${ben_path_data}${ben_path}/exception/${adate}${aclock[$j]}_exception.csv"

				#写入小时信息
	      echo "${adate}:${aclock[$j]}" >> ${checkreport}
				echo " " >> ${checkreport}
				echo "junjian_err:" >> ${checkreport}

				#将军建 err 统计写入errreport
				cat ${junjian_file_err} | awk 'BEGIN {FS=","} {printf "%s\n", $1}' | sort | uniq -c >> ${checkreport}

				#军建错误和 ben 老师错误分割线
				echo "-------------------------" >> ${checkreport}
				echo "ben_err:" >> ${checkreport}

				#ben 老师 err 统计写入 errreport
				cat ${ben_file_err} | awk 'BEGIN {FS="|"} {printf "%s\n", $1}' | sort | uniq -c >> ${checkreport}

	      #小时分割线
				echo "*************NEXT HOUR**************" >> ${checkreport}
		 done

done
