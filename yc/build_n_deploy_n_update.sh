#!/usr/bin/env bash

IAM_TOKEN=$(yc iam create-token)
CONTAINER_REGISTRY_URL='cr.yandex'
REGISTRY_NAME='docker-football'

IMAGE_NICK='football'
TAG='0.75'

docker login \
  --username iam \
  --password $IAM_TOKEN \
  $CONTAINER_REGISTRY_URL

REGISTRY_ID=$(yc container registry get $REGISTRY_NAME | head -n 1 | cut -d ' ' -f2)

IMAGE_NAME=$CONTAINER_REGISTRY_URL/$REGISTRY_ID/$IMAGE_NICK:$TAG

echo Start building ${IMAGE_NAME}
docker build . --no-cache -t $IMAGE_NAME
docker push $IMAGE_NAME

RUNNING_ID=$(yc compute instance get football | head -n 1 | grep id | cut -d ' ' -f2)

yc compute instance update-container ${RUNNING_ID} \
  --container-name=$CONTAINER_NAME \
  --container-image=$IMAGE_NAME \
