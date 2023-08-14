#!/bin/bash -xe


IMAGE="isucon13-portal"
TAG="$1"

if [ -z "$TAG" ];then
    TAG=develop
fi

docker build --platform linux/amd64 -t ${IMAGE}:${TAG} .
# docker push ${IMAGE}:${TAG}

