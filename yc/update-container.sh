#!/bin/bash

NAME='football'
TAG='0.74'
SERVICE_ACCOUNT_NAME='football-acc'
CONTAINER_NAME='football-flask'
CONTAINER_REGISTRY_URL='cr.yandex'
REGISTRY_NAME='docker-football'
REGISTRY_ID=$(yc container registry get $REGISTRY_NAME | head -n 1 | cut -d' ' -f2)
IMAGE_NAME=$CONTAINER_REGISTRY_URL/$REGISTRY_ID/$NAME:$TAG


RUNNING_ID=$(yc compute instance get football | head -n 1 | grep id | cut -d ' ' -f2)

yc compute instance update-container ${RUNNING_ID} \
  --container-name=$CONTAINER_NAME \
  --container-image=$IMAGE_NAME \
