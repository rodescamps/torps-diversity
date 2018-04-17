#!/bin/bash

# Example: sh run_simulations_vanilla_relay_adv.sh ../.. typical tor ../../out/network-states 50000 50000 0 5 5 1 270

BASE_DIR=$1
USERMODEL=$2
PATH_ALG=$3
NSF_ROOT_DIR=$4

ADV_GUARD_CONS_BW=$5
ADV_EXIT_CONS_BW=$6
ADV_TIME=$7
NUM_ADV_GUARDS=$8
NUM_ADV_EXITS=$9
NUM_GUARDS=${10}
GUARD_EXPIRATION=${11}

OUTPUT="relay-adv"
NUM_SAMPLES=50
TRACEFILE=$BASE_DIR/in/users2-processed.traces.pickle
LOGLEVEL="INFO"

PARALLEL_PROCESS=`nproc --all`
# PARALLEL_PROCESS=8

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
     nohup python ../pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL --format $OUTPUT --adv_guard_cons_bw $ADV_GUARD_CONS_BW --adv_exit_cons_bw $ADV_EXIT_CONS_BW --adv_time $ADV_TIME --num_adv_guards $NUM_ADV_GUARDS --num_adv_exits $NUM_ADV_EXITS --num_guards $NUM_GUARDS --guard_expiration $GUARD_EXPIRATION --loglevel $LOGLEVEL $PATH_ALG 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.error 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.$i.out &
  i=$(($i+1))
  done
done
