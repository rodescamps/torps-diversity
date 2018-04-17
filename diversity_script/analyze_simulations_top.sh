#!/bin/sh

# Example: sh analyze_simulations_top.sh ../../out/simulate/tor/typical.network-state-2018-01/out/network-adv/out ../../out/simulate/tor/typical.network-state-2018-01/network-adv/as/16276_guards ../../out/simulate/tor/typical.network-state-2018-01/network-adv/as/16276_exits ../../out/analysis/2018-01 16276
IN_DIR=$1
TOP_GUARDS_LIST=$2
TOP_EXITS_LIST=$3
OUT_DIR=$4
OUT_NAME=$5
nohup python ../pathsim_analysis.py simulation-top $IN_DIR $TOP_GUARDS_LIST $TOP_EXITS_LIST $OUT_DIR $OUT_NAME &
