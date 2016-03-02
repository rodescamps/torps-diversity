


BASE_DIR=$1
PATH_ALG=$2
NETWORKCASE=$3
METRIC=$4

SIM_DIR=$BASE_DIR/out/simulate/$NETWORKCASE/$PATH_ALG
OUT_DIR=$BASE_DIR/out/metric/
PARALLEL_PROCESS_MAX=24

DIRS=`ls -l $SIM_DIR | egrep '^d' | awk '{print $9}'`

j=1
mkdir -p $OUT_DIR/$NETWORKCASE/$PATH_ALG
for DIR in $DIRS
do
  if [ $j -eq $(($PARALLEL_PROCESS_MAX-1)) ]
  then
     pypy pathsim_metrics.py $METRIC $SIM_DIR/${DIR}/*.out >> $OUT_DIR/$NETWORKCASE/$PATH_ALG/$METRIC
    j=0
  else
     pypy pathsim_metrics.py $METRIC $SIM_DIR/${DIR}/*.out >> $OUT_DIR/$NETWORKCASE/$PATH_ALG/$METRIC &

  fi
  j=$(($j+1))
done
