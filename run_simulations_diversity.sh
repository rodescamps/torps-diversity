#!/bin/bash

BASE_DIR=$1
USERMODEL=$2
PATH_ALG=$3
NSF_ROOT_DIR=$4
OUTPUT=$5
NUM_SAMPLES=2500
NSF_TYPE="slim"
TRACEFILE=$BASE_DIR/in/users2-processed.traces.pickle
LOGLEVEL="INFO"
PARALLEL_PROCESS_MAX=20

DIRS=`ls -l $NSF_ROOT_DIR | egrep '^d' | awk '{print $9}'`
i=0
for DIR in $DIRS 
do 
  EXP_NAME=$USERMODEL.${DIR}
  NSF_DIR=$NSF_ROOT_DIR/${DIR}
  OUT_DIR=$BASE_DIR/out/simulate/$PATH_ALG/$EXP_NAME
  mkdir -p $OUT_DIR
  while [ $i -lt $PARALLEL_PROCESS ]
  do
      nohup time pypy pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.time 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.out &
  i=$(($i+1))
  done

done
