#!/bin/sh
# ./service/reprocess.sh 20151013 0 23
if [[ -e "/etc/pydota.conf" ]]; then
  . /etc/pydota_reprocess.conf
fi

if [[ -n "$HOME" && -e "$HOME/.pydota" ]]; then
  . "$HOME/pydota_reprocess"
fi
datetime=$1
start_hour=$2
end_hour=$3
topics=("mpp_vv_pcweb mpp_vv_mobile mpp_vv_mobile_new_version mpp_vv_pcclient mpp_vv_msite mpp_vv_padweb mpp_vv_ott ott_vv_41 ott_vv_44 mpp_vv_mobile_211_20151012 ott_vv_311_20151012")
cd $pydota_path
for topic in ${topics}; do
    ./service/script/py_dota_reprocess.sh $datetime $start_hour $end_hour  $topic &
done
