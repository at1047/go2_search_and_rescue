#!/bin/bash
set -e

xhost +local:docker

docker run -it \
    --net=host \
    --privileged \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    -e CYCLONEDDS_URI="<CycloneDDS><Domain><General><NetworkInterfaceAddress>192.168.123.10</NetworkInterfaceAddress></General></Domain></CycloneDDS>" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd)":/root/go2_docker \
    -w /root/go2_docker \
    ros2-go2:latest bash
