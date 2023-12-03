#!/usr/bin/env bash

IAM_TOKEN=$(yc iam create-token)
CONTAINER_REGISTRY_URL='cr.yandex'
REGISTRY_NAME='docker-football'

IMAGE_NICK='football'
TAG='0.8'

docker login \
  --username iam \
  --password $IAM_TOKEN \
  $CONTAINER_REGISTRY_URL

REGISTRY_ID=$(yc container registry get $REGISTRY_NAME | head -n 1 | cut -d ' ' -f2)

IMAGE_NAME=$CONTAINER_REGISTRY_URL/$REGISTRY_ID/$IMAGE_NICK:$TAG

echo Start building ${IMAGE_NAME}
docker build . -t $IMAGE_NAME
docker push $IMAGE_NAME