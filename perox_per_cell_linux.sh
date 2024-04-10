#!/bin/bash
file="/Users/betatester/SCRI/perox-per-cell/Experiment-0024.zvi"

POdotcut=0.0064
POminarea=1
POmaxintensity=16383

echo "Running perox-per-cell..."

# Set output directory for z-projections
zprojdircells="$file""_Zprojections/cells/"
zprojmasksdir="$file""_ZprojectionMasks/"

# Source conda, otherwise conda init error messages may appear. If needed, edit the
# location of conda.sh here using the output of the command
# > conda info | grep -i 'base environment'
source /opt/miniconda3/etc/profile.d/conda.sh 

# Activate virtual python environment for peroxisome segmentation
conda activate pseg

# Make z-projections and get peroxisome masks
python zproject_get_perox_masks.py "$file" $POdotcut $POminarea $POmaxintensity

# Deactivate python 3.10.0 environment
conda deactivate

# Activate virtual python environment for cell segmentation
conda activate cseg

# Get cell masks
python get_cell_masks_and_count.py "$file" "$zprojdircells" "$zprojmasksdir" $POdotcut $POminarea $POmaxintensity

# Deactivate Python 3.5 environment
conda deactivate

