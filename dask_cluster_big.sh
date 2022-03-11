#!/bin/sh
#SBATCH -p ProdQ
#SBATCH -N 8
#SBATCH -t 3-00:00:00
#SBATCH -A ichec004
#SBATCH --mail-user=james.nelson@ichec.ie
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END  

cd $SLURM_SUBMIT_DIR

module load intel/2020u4
module load conda

# $1 = number of workers + 1
# $2 = name of scheduler-file

echo "Starting Dask Cluster"
echo "With" $1 "-1 workers"
echo "Scheduler is" $2".json"
mpirun --np $1 dask-mpi --scheduler-file $2".json" #--interface ib0
echo "Dask Cluster stopped"

