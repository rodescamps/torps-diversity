#!/bin/sh

# Example: sh analyze_simulations_set.sh ../../out/simulate/tor/typical.network-state-2018-01/out/network-adv/out ../../out/analysis/2018-01 DE ../../out/simulate/tor/typical.network-state-2018-01/network-adv/countries/DE
# Example: sh analyze_simulations_set.sh ../../out/simulate/tor/typical.network-state-2018-01/out/relay-adv/out ../../out/analysis/2018-01 relay-adv
IN_DIR=$1
OUT_DIR=$2
OUT_NAME=$3
SET_FILE=$4
if [ -n "$4" ]; then
  nohup python ../pathsim_analysis.py simulation-set $IN_DIR $OUT_DIR $OUT_NAME $SET_FILE &
else
  nohup python ../pathsim_analysis.py simulation-set $IN_DIR $OUT_DIR $OUT_NAME &
fi
