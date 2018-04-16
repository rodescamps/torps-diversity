#!/bin/sh

# Example: sh generate_plots.sh top ../../analysis/ ../../out/plots custom_name

PLOT_TYPE=$1
IN_DIR=$2
OUT_DIR=$3
OUT_NAME=$4
python ../pathsim_plot.py $PLOT_TYPE $IN_DIR $OUT_DIR $OUT_NAME
