#!/bin/sh
# 从raw数据中计算各个平台每个小时的数据
# py_dota_report_vv_detail_plid_cid.sh 20151007
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/.pydota"
fi

#设置bearychat发送目标为dota-日报
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/4dc6e829b29d810a677f67af1c1e945f"

if [ $# -eq 1 ];then
    start_time=$1
else
    start_time=`date +%Y%m%d`
fi

clienttypes=(android iphone pcweb ipad apad phonem ott pcclient padweb)
clienttypes_tmp=`echo ${clienttypes[*]}`

sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path=${sub_path_year}/${sub_path_month}
work_path="${pydota_path}"
bearychat="${work_path}/bin/bearychat.sh"

cd $work_path

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


function report_vv_plid_cid(){
    # 当一天运行完成后，开始统计

    while true
    do
        len=${#clienttypes[@]}
        if [ ${len} -eq 0 ];then
            break
        fi

        for clienttype in ${clienttypes[@]};
        do
            filename=${start_time}_vv_${clienttype}_vid.csv
            if [ -f ${pydota_dailyreport}/${sub_path}/.done_${filename} ]; then
                echo "DATE,TIME,CID,PLID,PT,LN,CLIENTTP,CLIENTVER,VV" >${pydota_dailyreport}/${sub_path}/${start_time}_vv_${clienttype}_plid.csv
                echo "DATE,TIME,CID,PT,LN,CLIENTTP,CLIENTVER,VV" >${pydota_dailyreport}/${sub_path}/${start_time}_vv_${clienttype}_cid.csv

                # 计算plid纬度表
                cat ${pydota_dailyreport}/${sub_path}/${filename} |sed "1d"| awk -F, '{
                type=$1","$2","$3","$4","$6","$7","$8","$9;
                if(!(type in sum)){
                sum[type]=0};
                sum[type]=sum[type]+$NF
                }
                END{
                for(i in sum) {
                print sum[i]" "i
                }
                }'|awk '{print $2","$1}' \
                >> ${pydota_dailyreport}/${sub_path}/${start_time}_vv_${clienttype}_plid.csv

                # 计算cid纬度表
                cat ${pydota_dailyreport}/${sub_path}/${filename}|sed "1d" | awk -F, 'BEGIN{
                meizi_dict[1]="综艺";
                meizi_dict[2]="电视剧";
                meizi_dict[3]="电影";
                meizi_dict[4]="音乐";
                meizi_dict[5]="纪录片";
                meizi_dict[6]="原创";
                meizi_dict[7]="动漫";
                meizi_dict[8]="生活";
                meizi_dict[9]="女性";
                meizi_dict[10]="新闻";
                meizi_dict[119]="品牌专区";
                meizi_dict[82]="ott一级分类";
                meizi_dict[83]="ott电视剧";
                meizi_dict[84]="ott电影";
                meizi_dict[85]="ott纪实";
                meizi_dict[86]="ott音乐";
                meizi_dict[87]="ott综艺";
                meizi_dict[88]="ott动漫";
                meizi_dict[92]="ott广告";
                meizi_dict[97]="ott教育";
                meizi_dict[98]="ott体育";
                meizi_dict[99]="ott财经";
                meizi_dict[100]="ott生活";
                meizi_dict[101]="ott微电影";
                meizi_dict[102]="ott品牌专区";
                meizi_dict[112]="ott-IPTV轮播";
                meizi_dict[113]="ott快乐购";
                }
                {
                if($3 in meizi_dict)
                {type=$1","$2","meizi_dict[$3]","$6","$7","$8","$9;}
                else{type=$1","$2",其他,"$6","$7","$8","$9;}
                if(!(type in sum)){
                sum[type]=0};
                sum[type]=sum[type]+$NF
                }
                END{
                for(i in sum) {
                print sum[i]" "i
                }
                }'|awk '{print $2","$1}' \
                >> ${pydota_dailyreport}/${sub_path}/${start_time}_vv_${clienttype}_cid.csv


                xrsh_arritemidx "$clienttypes_tmp" "$clienttype"
                i=$?
                unset clienttypes[$i]

            fi
        done
    # while
    done
}

report_vv_plid_cid
