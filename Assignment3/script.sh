#!/bin/bash
#SBATCH --partition=GPU
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=gpu02
#SBATCH --gpus=1
#SBATCH --mem=20G
#SBATCH --job-name="Deep_Learning_Q2New"
#SBATCH --output=q2outNew.out
#SBATCH --error=q2errNew.err
#SBATCH --mail-user=teewz1076@UWEC.EDU
#SBATCH --mail-type=END


module load python/3.9.2
module load python-libs/3.0
module load python

python q2.py