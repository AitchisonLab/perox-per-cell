#!/bin/bash
 
echo "Loading perox-per-cell..."
SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Source conda, otherwise conda init error messages may appear. If needed, edit the
# location of conda.sh here using the output of the command
# > conda info | grep -i 'base environment'
source /Users/maxneal/opt/anaconda3/etc/profile.d/conda.sh

continue=1

while [ $continue -gt 0 ]

do
        # Activate virtual python environment for peroxisome segmentation
		echo "Loading environment for peroxisome segmentation"

        conda activate pseg

        # Make z-projections and get peroxisome masks
        python zproject_get_perox_masks.py "$SCRIPTDIR"/

        # Deactivate python 3.10.0 environment
        conda deactivate

        # Set configuration file target location
        configfile="$SCRIPTDIR"/ppc_job_config.json

        # See if configuration file has been written out
        if test -f "$configfile"; then

                # Activate virtual python environment for cell segmentation
				echo "Loading environment for cell segmentation"

                conda activate cseg

                # Get cell masks
                python get_cell_masks_and_count.py "$configfile"

                # Deactivate Python 3.5 environment
                conda deactivate
        fi

        if test -f "$configfile"; then  # Make sure we clean up loose configuration files
                rm "$configfile"
                continue=1  # Program just ran, reopen for more jobs
        else
                continue=0  #Program was closed
        fi

done
