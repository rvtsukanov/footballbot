#!/bin/bash

NAME='football'
TAG='0.7'
SERVICE_ACCOUNT_NAME='football-acc'
CONTAINER_NAME='football-flask'
CONTAINER_REGISTRY_URL='cr.yandex'
REGISTRY_NAME='docker-football'
REGISTRY_ID=$(yc container registry get $REGISTRY_NAME | head -n 1 | cut -d' ' -f2)
IMAGE_NAME=$CONTAINER_REGISTRY_URL/$REGISTRY_ID/$NAME:$TAG

DISK_SIZE_GB=30
DISK_NAME=football-disk-main-${DISK_SIZE_GB}

# Check if disk already exists
EXIST_DISK_NAME=$(yc compute disk list | grep ${DISK_NAME})
echo "Checking ${EXIST_DISK_NAME}"

if [ -z ${EXIST_DISK_NAME} ]
then
  echo "DISK ${DISK_NAME} NOT FOUND. CREATING."  # TBD:(
  yc compute disk create \
  --name ${DISK_NAME} \
  --size ${DISK_SIZE_GB} \
  --zone ru-central1-a
else
  echo "DISK ${DISK_NAME} FOUND. USING EXISTING."
fi


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
  --zone ru-central1-a \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --service-account-name $SERVICE_ACCOUNT_NAME \
  --platform standard-v3 \
  --public-ip \
  --container-name=$CONTAINER_NAME \
  --container-image=$IMAGE_NAME \
  --container-stdin \
  --container-tty \
  --attach-disk disk-name=${DISK_NAME}




