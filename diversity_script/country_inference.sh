#!/bin/sh

# Example: sh country_inference.sh DE ../../out/simulate/tor/typical.network-state-2018-01/network-adv/out ../../out/simulate/tor/typical.network-state-2018-01/network-adv/country

COUNTRY=$1
IN_DIR=$2
OUT_DIR=$3
mkdir -p $OUT_DIR
nohup python ../country_inference.py $COUNTRY $IN_DIR $OUT_DIR &