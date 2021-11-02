#!/bin/bash
#SBATCH --partition=GPU
#SBATCH --time=5:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=gpu02
#SBATCH --mem=20G
#SBATCH --job-name="Deep_Learning_Q2"
#SBATCH --output=q2out.out
#SBATCH --error=q2err.err
#SBATCH --mail-user=teewz1076@UWEC.EDU
#SBATCH --mail-type=END


module load python/3.9.2
module load python-libs/3.0

python q2.py