#!/bin/sh

# Example: sh analyze_simulations.sh simulation-top ../../out/simulate/tor/typical.network-state-2017-01/ ../../top_guards ../../top_exits ../../out/analysis custom_name

PLOT_TYPE=$1
IN_DIR=$2
TOP_GUARDS_LIST=$3
TOP_EXITS_LIST=$4
OUT_DIR=$5
OUT_NAME=$6
nohup pypy pathsim_analysis.py $PLOT_TYPE $IN_DIR $TOP_GUARDS_LIST $TOP_EXITS_LIST $OUT_DIR $OUT_NAME &