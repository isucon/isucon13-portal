#!/bin/bash -xe


IMAGE="424484851194.dkr.ecr.ap-northeast-1.amazonaws.com/isucon13-portal"
TAG="$1"

if [ -z "$TAG" ];then
    TAG=develop
fi

docker build --platform linux/amd64 -t ${IMAGE}:${TAG} .
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 424484851194.dkr.ecr.ap-northeast-1.amazonaws.com
docker push ${IMAGE}:${TAG}

