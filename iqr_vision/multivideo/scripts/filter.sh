#!/bin/bash
source /ros_entrypoint.sh
find * -type f -exec rosbag filter {} filtered_{} 'topic == "/device_0/sensor_1/Color_0/image/data"' \;
mkdir -p /filtered_bags
mv filtered_* /filtered_bags/