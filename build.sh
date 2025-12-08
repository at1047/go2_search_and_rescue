#!/bin/bash

set -e  # exit on error

IMAGE_NAME="ros2-go2"
TAG="latest"

echo "Building Docker image: $IMAGE_NAME:$TAG"

docker build \
    -t ${IMAGE_NAME}:${TAG} \
    .

echo "Build completed successfully: ${IMAGE_NAME}:${TAG}"
