#!/bin/bash

NAME='football'
TAG='0.5'
SERVICE_ACCOUNT_NAME='football-acc'
CONTAINER_NAME='football-flask'
CONTAINER_REGISTRY_URL='cr.yandex'
REGISTRY_NAME='docker-football'
REGISTRY_ID=$(yc container registry get $REGISTRY_NAME | head -n 1 | cut -d' ' -f2)
IMAGE_NAME=$CONTAINER_REGISTRY_URL/$REGISTRY_ID/$NAME:$TAG

# Delete running
RUNNING_ID=$(yc compute instance get football | head -n 1 | grep id | cut -d ' ' -f2)
echo Running ID ${RUNNING_ID}

if [ -z ${RUNNING_ID} ]
then
  echo "Nothing to delete"
else
  echo deleting ${RUNNING_ID}
  yc compute instance delete ${RUNNING_ID}
fi


yc compute instance create-with-container \
  --name $NAME \
  --zone ru-central1-b \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --service-account-name $SERVICE_ACCOUNT_NAME \
  --platform standard-v3 \
  --create-boot-disk size=30 \
  --public-ip \
  --container-name=$CONTAINER_NAME \
  --container-image=$IMAGE_NAME \
  --container-stdin \
  --container-tty




