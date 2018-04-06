#!/bin/sh

# Example: sh as_inference.sh 16276 ../../out/simulate/tor/typical.network-state-2017-01/out/ ../../out/simulate/tor/typical.network-state-2017-01/as

AS=$1
IN_DIR=$2
OUT_DIR=$3
nohup pypy ../as_inference.py $AS $IN_DIR $OUT_DIR &