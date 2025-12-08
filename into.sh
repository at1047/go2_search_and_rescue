#!/bin/bash

set -e

CONTAINER_NAME="go2_dev"

# Check if container is running
RUNNING=$(docker ps --filter "name=${CONTAINER_NAME}" --format "{{.ID}}")

if [ -n "$RUNNING" ]; then
    echo "Attaching to running container: $CONTAINER_NAME"
    docker exec -it $CONTAINER_NAME bash
else
    echo "No running container found. Starting a new one..."
    
    xhost +local:docker

    docker run -it \
        --net=host \
        --env DISPLAY=$DISPLAY \
        --env QT_X11_NO_MITSHM=1 \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v $(pwd):/root/go2_docker \
        -w /root/go2_docker \
        --name ${CONTAINER_NAME} \
        ros2-go2:latest bash
fi
