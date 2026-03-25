#!/bin/bash
#SBATCH -J abaqus_test   #作业名
#SBATCH -p Agent0
#SBATCH -N 1   #节点数
#SBATCH --ntasks-per-node=10 #每节点进程数
#SBATCH -o out.%j    
#SBATCH -e err.%j

module purge
source ~/apprepo/abaqus/2022-null/scripts/env.sh
export EXEC=$PROGLIST
WORK_DIR=`pwd`     #当前目录
INPUT_FILE=input_001.inp  #输入文件
job_name=`echo ${INPUT_FILE} | awk -F. '{print $1}'`
#USER_FILE=exa_fml_ortho_damage_umat.for    #fortran子程序
LOG_FILE=abaqus-test.log   
#########################################################

cd $WORK_DIR  
PROCS=$SLURM_NPROCS
env_file=abaqus_v6.env
node_list=$(scontrol show hostname ${SLURM_NODELIST} | sort -u)

mp_host_list="["
for host in ${node_list}; do
    mp_host_list="${mp_host_list}['$host', ${SLURM_CPUS_ON_NODE}],"
done

mp_host_list=$(echo ${mp_host_list} | sed -e "s/,$/"]")

echo "mp_host_list=${mp_host_list}"  >${env_file}
echo "mp_mpi_implementation=IMPI" >>${env_file} 
echo "mp_file_system=(SHARED, LOCAL)" >>${env_file}


echo The start time is: `date +"%Y-%m-%d %H:%M:%S"` | tee $LOG_FILE  
echo My job ID is: $SLURM_JOB_ID | tee -a $LOG_FILE 
echo The total cores is: $PROCS | tee -a $LOG_FILE 
echo The hosts is: | tee -a $LOG_FILE 
cat $HOST_FILE | tee -a $LOG_FILE


############程序主命令
#ssh $HOSTNAME "source /public/software/compiler/intel/intel-compiler-2017.5.239/bin/compilervars.sh intel64;cd $WORK_DIR;$EXEC job=${job_name} input=${INPUT_FILE} user=$USER_FILE cpus=${PROCS} mp_mode=MPI double int"

$EXEC job=${job_name} input=${INPUT_FILE} cpus=${PROCS} mp_mode=MPI   int

#ssh $HOSTNAME "export LM_LICENSE_FILE=27800@hlogin11;cd $WORK_DIR;$EXEC job=${job_name} input=${INPUT_FILE} cpus=${PROCS} mp_mode=THREAD double int"

echo The end time is: `date +"%Y-%m-%d %H:%M:%S"` | tee -a $LOG_FILE  