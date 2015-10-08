#!/bin/bash
#$1 is time
#$2 is topic list such as: mpp_vv_pcweb, mpp_vv_mobile, mpp_vv_mobile_new_version, mpp_vv_pcclient, mpp_vv_msite, mpp_vv_padweb, mpp_vv_ott, ott_vv_41, ott_vv_44

junjian_path_orig="/home/junjian/pydota/orig/"
junjian_path_des="/home/junjian/pydota/des/"
junjian_path_report="/home/junjian/pydota/report/"
#ben_path_orig="/data/matrix/"
#ben_path_des=""
#ben_path_report="/data/marix/result/"

#echo ${junjian_path_report}

if [ "$2" ]; then
        if [ "$2" == "mpp_vv_pcweb" ]; then
                ben_path_orig="/data/matrix/pcp/raw/"
                ben_path_des="/data/matrix/pcp/data/"
                ben_path_err="/data/matrix/pcp/exception/"
        elif [ "$2" == "mpp_vv_mobile" ]; then
                ben_path_orig="/data/matrix/mobile_old/raw/"
                ben_path_des="/data/matrix/mobile_old/data/"
                ben_path_err="/data/matrix/mobile_old/exception/"
        elif [ "$2" == "mpp_vv_mobile_new_version" ]; then
                ben_path_orig="/data/matrix/mobile/raw/"
                ben_path_des="/data/matrix/mobile/data/"
                ben_path_err="/data/matrix/mobile/exception/"
        elif [ "$2" == "mpp_vv_pcclient" ]; then
                ben_path_orig="/data/matrix/pcc/raw/"
                ben_path_des="/data/matrix/pcc/data/"
                ben_path_err="/data/matrix/pcc/exception/"
        elif [ "$2" == "mpp_vv_msite" ]; then
                ben_path_orig="/data/matrix/mz/raw/"
                ben_path_des="/data/matrix/mz/data/"
                ben_path_err="/data/matrix/mz/exception/"
        elif [ "$2" == "mpp_vv_padweb" ]; then
                ben_path_orig="/data/matrix/padweb/raw/"
                ben_path_des="/data/matrix/padweb/data/"
                ben_path_err="/data/matrix/padweb/exception/"
        elif [ "$2" == "mpp_vv_ott" ]; then
                ben_path_orig="/data/matrix/ott/raw/"
                ben_path_des="/data/matrix/ott/data/"
                ben_path_err="/data/matrix/ott/exception/"
        elif [ "$2" == "ott_vv_41" ]; then
		ben_path_orig="/data/matrix/ott41/raw/"
                ben_path_des="/data/matrix/ott41/data/"
                ben_path_err="/data/matrix/ott41/exception/"
	elif [ "$2" == "ott_vv_44" ]; then
		ben_path_orig="/data/matrix/ott44/raw/"
                ben_path_des="/data/matrix/ott44/data/"
                ben_path_err="/data/matrix/ott44/exception/"
	fi
fi

echo ${ben_path_des}
echo ${ben_path_orig}


