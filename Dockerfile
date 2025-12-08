FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ----------------------------------------------------------
# Locale + basic utilities
# ----------------------------------------------------------
RUN apt update && apt install -y \
    locales \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    nano \
    vim \
    iputils-ping \
    net-tools \
    mesa-utils \
    x11-apps \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

RUN locale-gen en_US en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# ----------------------------------------------------------
# FORCE PYTHON 3.10 DEFAULT
# ----------------------------------------------------------
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --set python /usr/bin/python3.10
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# ----------------------------------------------------------
# Install ROS2 Humble for Ubuntu 22.04
# ----------------------------------------------------------
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/ros2.list

RUN apt update && apt install -y \
    ros-humble-desktop \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    python3-colcon-common-extensions

# ----------------------------------------------------------
# ADD THIS: install CycloneDDS runtime tools (optional but safe)
# ----------------------------------------------------------
RUN apt install -y cyclonedds-tools || true

# ----------------------------------------------------------
# CycloneDDS configuration
# ----------------------------------------------------------
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# ----------------------------------------------------------
# Auto source ROS2 on startup
# ----------------------------------------------------------
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

ENV PYTHONUNBUFFERED=1
