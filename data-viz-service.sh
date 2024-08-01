#!/bin/bash
#=========================================================================
# Copyright (C) Atos - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
#=========================================================================

IMAGE_NAME="data-viz-cvlab"
VERSION="0.1"
CNAME="data-viz-cvlab"

ERROR="Error: please enter build | start | stop | in | incvlab" 
HOST=$(hostname -f)

case "$1" in
    "start")
		docker run -it --rm  \
			-d  \
			-w /data1/home/moring/ \
			-v /data1:/data1 \
			-v /sandbox:/sandbox \
			--net=host --gpus all \
			--ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
			-h $CNAME-$VERSION-$HOST  \
			--name ${CNAME} \
			-e https_proxy=http://$https_proxy \
			-e http_proxy=http://$http_proxy \
			$IMAGE_NAME:$VERSION \
			sleep infinity
			
		;;
	"stop")     
		echo  "stop $CNAME "
		docker stop $CNAME
		;; 
    "in") 
		docker exec -ti  --user $(id -u):$(id -g) $CNAME bash
		;;
	"inroot") 
		docker exec -ti  --user root $CNAME bash
		;;
	*)
		echo $ERROR
		;;
esac
