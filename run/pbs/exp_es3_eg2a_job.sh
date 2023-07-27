#!/bin/bash
#PBS -N exp_es3_eg2a_job
#PBS -l ncpus=1
#PBS -l mem=500mb
#PBS -l walltime=02:00:00
#PBS -m ea
#PBS -WMail_Users=__USER_EMAIL__
#PBS -o /scratch/__USER__/pbs/
#PBS -e /scratch/__USER__/pbs/

trap "echo "---------------------"$'\r'; qstat -f $PBS_JOBID" EXIT


IFS='.' read -ra JOBID_ARRAY <<< $PBS_JOBID
PARENT_JOBID=${JOBID_ARRAY[0]}

JOBID=${PARENT_JOBID}_0
JOB_DIR=$JOBID

DATA_DIR=~/es3/es3_eg2/data/es3_eg2a/$PARENT_JOBID/$JOB_DIR
echo "SHELL:: Creating DATA_DIR: " $DATA_DIR
mkdir -p $DATA_DIR


SCRATCH_DIR=/scratch/$USER
SCRATCH_JOB_DIR=$SCRATCH_DIR/$JOBID
echo "SHELL:: Creating SCRATCH_JOB_DIR: " $SCRATCH_JOB_DIR
mkdir $SCRATCH_JOB_DIR








module load EasyBuild/4.2.2
module load Python/3.7.4-GCCcore-8.3.0

cd ~/virtualenvs/agent_model/bin
source activate

cd ${PBS_O_WORKDIR}


python3 -m run.exp.exp_es3_eg2a -j $PBS_JOBID -s $SCRATCH_DIR -w 'es3_eg2a' -a 'es3_eg2a_qlearning_asymmetric' -k true -z false -v true


cd $SCRATCH_DIR || exit 1

ARCHIVE_FILENAME=$JOBID.tar.gz
echo "SHELL:: creating archive: " $ARCHIVE_FILENAME
tar --remove-files --create --gzip --file=$ARCHIVE_FILENAME -C $SCRATCH_DIR $JOB_DIR

echo "SHELL:: moving archive ..."
mv -fv $ARCHIVE_FILENAME $DATA_DIR




echo "SHELL:: Finished."
