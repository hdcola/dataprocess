#!/bin/sh
# 从raw数据中计算各个平台一天总VV数据
# py_dota_report_total.sh 20151007

#设置bearychat发送目标为dota-日报
export BEARYCHAT_WEBHOOK="https://hook.bearychat.com/=bw7by/incoming/5a3d3583ecb52af13590a801bab94aa9"

if [ $# -ge 1 ];then
    start_time=$1
else
    start_time=`date -d yesterday +%Y%m%d`
fi
sub_path_year=${start_time:0:4}
sub_path_month=${start_time:4:2}
sub_path_day=${start_time:6:2}
sub_path_hour=${start_time:8:2}

clienttypes=(android iphone pcweb ipad apad phonem ott pcclient padweb win10client macclient)


sub_path=${sub_path_year}/${sub_path_month}
work_path="/home/xuguodong/pydota/pydota"
pydota_des="/home/xuguodong/data/des"
pydota_report="/home/xuguodong/data/dailyreport"

mkdir -p ${pydota_report}/${sub_path} 2>/dev/null

cd $work_path

function report_vv_vid(){
    proctime=`date "+%Y/%m/%d %H:%M:%S"`

    filenameraw=${start_time}*

    files=`ls ${pydota_des}/${sub_path}/${filenameraw} | grep -v "live"`

    cat ${files} | awk -F, -v start_time=${start_time} '{
    if($21=="play" && $1==start_time){
      print $1","substr($2,1,2)","$11","$12","$13","$17","$18","$22","$23}
    }' | sort | uniq -c | sort -rn |awk '{print $2","$1}' | awk -F',' \
    -v file=${pydota_report}/${sub_path}/${start_time}"_vv_" '{print $0 >>file$8"_vid.csv"}'

    for clienttype in ${clienttypes[@]};
    do
        filename=${start_time}_vv_${clienttype}_vid.csv
        if [ -f ${pydota_report}/${sub_path}/${filename} ]; then
            cat ${pydota_report}/${sub_path}/${filename} | sort -n > ${pydota_report}/${sub_path}/${filename}
            sed -i '1i\DATE,TIME,CID,PLID,VID,PT,LN,CLIENTTP,CLIENTVER,VV'  ${pydota_report}/${sub_path}/${filename}
            echo "DATE,TIME,CID,PLID,PT,LN,CLIENTTP,CLIENTVER,VV" >${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_plid.csv
            echo "DATE,TIME,CID,PT,LN,CLIENTTP,CLIENTVER,VV" >${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_cid.csv

            # 计算plid纬度表
            cat ${pydota_report}/${sub_path}/${filename} |sed "1d"| awk -F, '{
            type=$1","$2","$3","$4","$6","$7","$8","$9;
            if(!(type in sum)){
            sum[type]=0};
            sum[type]=sum[type]+$NF
            }
            END{
            for(i in sum) {
            print sum[i]" "i
            }
            }'|awk '{print $2","$1}' | sort -n \
            >> ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_plid.csv

            # 计算cid纬度表
            cat ${pydota_report}/${sub_path}/${filename}|sed "1d" | awk -F, 'BEGIN{
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
            }'|awk '{print $2","$1}' | sort -n \
            >> ${pydota_report}/${sub_path}/${start_time}_vv_${clienttype}_cid.csv
        fi
    done

}
report_vv_vid