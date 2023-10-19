#!/bin/bash

NAME='football'
DESC=""

yc compute instance create \
      --name=$NAME \
      --description=$DESC \
      --public-ip \
      --create-disk "size=128" \

