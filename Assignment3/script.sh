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


module load miniconda3
module load seaborn
module load Image

python q2.py