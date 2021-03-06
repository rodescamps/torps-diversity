#!/bin/bash

# Example: sh run_simulations_vanilla_network_adv.sh ../.. typical tor ../../out

BASE_DIR=$1
USERMODEL=$2
PATH_ALG=$3
NSF_ROOT_DIR=$4
OUTPUT="network-adv"
NUM_SAMPLES=50
TRACEFILE=$BASE_DIR/in/users2-processed.traces.pickle
LOGLEVEL="INFO"

PARALLEL_PROCESS=`nproc --all`

DIRS=`ls -l $NSF_ROOT_DIR | egrep '^d' | awk '{print $9}'`
i=0
for DIR in $DIRS 
do 
  EXP_NAME=$USERMODEL.${DIR}
  NSF_DIR=$NSF_ROOT_DIR/${DIR}
  OUT_DIR=$BASE_DIR/out/simulate/$PATH_ALG/$EXP_NAME/$OUTPUT/out
  mkdir -p $OUT_DIR
  while [ $i -lt $PARALLEL_PROCESS ]
  do
      nohup python ../pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.error 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.out &
  i=$(($i+1))
  done

done
