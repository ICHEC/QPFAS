#!/bin/sh
#SBATCH -p DevQ
#SBATCH -N 2
#SBATCH -t 01:00:00
#SBATCH -A ichec004

cd $SLURM_SUBMIT_DIR

module load intel/2020u4
module load conda

echo "Starting Dask Cluster"
mpirun --np 21 dask-mpi --scheduler-file scheduler.json --interface ib0
echo "Dask Cluster stopped"

