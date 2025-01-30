#!/bin/bash

cd $(dirname $0)
mkdir -p build
cd build
cmake -D CMAKE_INSTALL_PREFIX:PATH=~/opt/iqr-vision-utils/ ..
make -j4
make install