


BASE_DIR=$1
USERMODEL=$2
PATH_ALG=$3
NSF_ROOT_DIR=$4
OUTPUT="normal"
NUM_SAMPLES=50000
NSF_TYPE="slim"
TRACEFILE=$BASE_DIR/in/users2-processed.traces.pickle
LOGLEVEL="INFO"
PARALLEL_PROCESS_MAX=22
NETWORKCASE="3aE=SGM"
WF_OPTIMAL="--wf_optimal"

DIRS=`ls -l $NSF_ROOT_DIR | egrep '^d' | awk '{print $9}'`
j=1
for DIR in $DIRS 
do 
  EXP_NAME=$USERMODEL.${DIR}
  NSF_DIR=$NSF_ROOT_DIR/${DIR}
  OUT_DIR=$BASE_DIR/out/simulate/$NETWORKCASE/$PATH_ALG/$EXP_NAME
  mkdir -p $OUT_DIR
  if [ $j -eq $(($PARALLEL_PROCESS_MAX-1)) ]
  then
   
      (time pypy pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL $WF_OPTIMAL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG) 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.time 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.out
      j=0
  else
      (time pypy pathsim.py simulate --nsf_dir $NSF_DIR --num_samples $NUM_SAMPLES --trace_file $TRACEFILE --user_model $USERMODEL $WF_OPTIMAL --format $OUTPUT --loglevel $LOGLEVEL $PATH_ALG) 2> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.time 1> $OUT_DIR/simulate.$EXP_NAME.$NUM_SAMPLES-samples.out &
  fi
  j=$(($j+1))

done
