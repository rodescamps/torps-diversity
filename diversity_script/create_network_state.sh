#!/bin/sh

# Example: sh create_network_state.sh 2017 1 2017 1 ../../in ../../out ../../in/server-descriptors-2016-12

START_YEAR=$1
START_MONTH=$2
END_YEAR=$3
END_MONTH=$4
IN_DIR=$5
OUT_DIR=$6
INIT_DIR=$7
pypy pathsim.py process --slim --start_year $START_YEAR --start_month $START_MONTH --end_year $END_YEAR --end_month $END_MONTH --in_dir $IN_DIR --out_dir $OUT_DIR --initial_descriptor_dir $INIT_DIR