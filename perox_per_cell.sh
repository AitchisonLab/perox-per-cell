#!/bin/bash
file="[enter file path here]"

POdotcut=0.0064
POminarea=1
POmaxintensity=16383

# Set output directory for z-projections
zprojdircells="$file""_Zprojections/cells/"
zprojmasksdir="$file""_ZprojectionMasks/"

# Run the file that makes the z-projections and the peroxisome masks
/c/Users/mneal1/AppData/Local/Programs/Python/Python310/python.exe zproject_get_perox_masks.py "$file" $POdotcut $POminarea $POmaxintensity

# Activate Python 3.5.4 virtual environment
source /c/Users/mneal1/Desktop/Python_3_5_4_virtualenv/Scripts/activate

python --version

# Get cell masks
python get_cell_masks_and_count.py "$file" "$zprojdircells" "$zprojmasksdir" $POdotcut $POminarea $POmaxintensity

# Deactivate Python 3.5 environment
deactivate

