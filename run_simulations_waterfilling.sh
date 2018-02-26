#!/bin/bash


BASE_DIR=$1
USERMODEL=$2
PATH_ALG=$3
NSF_ROOT_DIR=$4
OUTPUT="normal"
NUM_SAMPLES=50000
NSF_TYPE="slim"
TRACEFILE=$BASE_DIR/in/users2-processed.traces.pickle
LOGLEVEL="INFO"
PARALLEL_PROCESS=10
PARALLEL_PROCESS_MAX=48

DIRS=`ls -l $NSF_ROOT_DIR | egrep '^d' | awk '{print $9}'`
j=1
for DIR in $DIRS 
do
  EXP_NAME=$USERMODEL.${DIR}.$PATH_ALG
  NSF_DIR=$NSF_ROOT_DIR/${DIR}
  OUT_DIR=$BASE_DIR/out/simulate/$EXP_NAME
  mkdir -p $OUT_DIR
  i=1
  while [ $i -lt $PARALLEL_PROCESS ]
  do
    if [ $j -le $(($PARALLEL_PROCESS_MAX-1)) ]
    then
      # wait this process to finish
      (time pypy pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG) 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.time 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.out
      j=0
    else
      # parallelize process
      (time pypy pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG) 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.time 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.out &
    fi
    i=$(($i+1))
    j=$(($j+1))

  done
done
