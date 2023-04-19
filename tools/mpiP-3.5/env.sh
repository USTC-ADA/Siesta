#!/bin/bash
export LDFLAGS="-L/home/yantao/common/papi/lib -lpapi"
export CPPFLAGS="-I/home/yantao/common/papi/include -I/home/yantao/common/libunwind-1.5.0/include -I/home/yantao/common/binutils-2.34/include"
./configure --prefix=/data/yantao/mpip-onlysum
make
make install
