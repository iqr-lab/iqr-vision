#!/bin/bash
nohup ~/opt/iqr-vision-utils/bin/iqr-multivideo -f $1 -t $2 > /dev/null 2>&1 &
echo $!