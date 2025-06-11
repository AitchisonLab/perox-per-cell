#!/usr/bin/env python
# coding: utf-8
# !!! NEEDS TO BE RUN FROM VIRTUALENV PYTHON_3_5 !!!
import os
import sys
import json
import warnings
import gc
import quantify_POs_per_cell

from mrcnnORIG.preprocess_images import preprocess_images
from mrcnnORIG.my_inference import predict_images
from mrcnnORIG.convert_to_image import convert_to_image
from skimage.measure import label

warnings.filterwarnings("ignore")

configloc = sys.argv[1]  # Configuration file for job
print("Working from configuration file at " + configloc)
print("Using yeast_segmentation to segment cells...")

# Read in job configuration file
configdata = json.load(open(configloc))
path = configdata.get('Path')
selectedhead, selectedtail = os.path.split(path)

processdir = int(configdata.get("ProcessDir"))  # Whether to process all other files in directory
POdotcut = float(configdata.get("PeroxSensitivity"))  # Peroxisome segmentation sensitivity parameter
POminarea = int(configdata.get("MinPeroxArea"))  # Minimum area for peroxisomes
cellminarea = int(configdata.get("MinCellArea"))  # Minimum area for cells
maxintensity = int(configdata.get("MaxIntensity"))  # Theoretical maximum intensity level of input images
version = configdata.get("Version")  # Software version

# If we're processing all files in a directory, add them all to a queue
if processdir == 1:
	paths = []
	filenames = os.listdir(selectedhead)
	for f in filenames:
		paths.append(os.path.join(selectedhead, f))
else:
	paths = [path]


def detect_cells(thepath):
	# How to skip if the necessary files aren't there (could have been skipped b/c not valid imaging file)
	head, tail = os.path.split(thepath)
	inputdir = head + "/" + tail + "_Zprojections/cells/"  # directory for z-projection of cells channel

	if not os.path.exists(inputdir):
		print("Skipping cell segmentation for " + thepath + ": Z-projection folder not present.")
		return

	maskdir = head + "/" + tail + "_ZprojectionMasks/"  # Directory for z-projection masks

	if not os.path.exists(maskdir):
		os.makedirs(maskdir)

	mainoutputdir = maskdir
	imageinfooutputfile = inputdir + "imageinfo.csv"
	predoutputfile = inputdir + "predictionsinfo.csv"

	print('Pre-processing...')
	processed = preprocess_images(inputdir, mainoutputdir, imageinfooutputfile, verbose=False)

	# Arguments:
	# test_path: Path where the images are stored (preprocess these using preprocess_images.py)
	# inputfile: Path of the comma-delimited file of images names.
	# outputfile: Path to write the comma-delimited run-length file to.
	# rescale: Set to True if rescale images before processing (saves time)
	# scale_factor: Multiplier to downsample images by
	# verbose: Verbose or not (true/false)'''
	# def predict_images(inputdir, outputfile, predoutputfile, rescale = False, scale_factor = 2, verbose = True):
	print('Predicting...')
	image_df = predict_images(mainoutputdir, imageinfooutputfile, predoutputfile, rescale=True, scale_factor=1)

	# Converts the compression rle files to images.
	# Input:
	# rlefile: csv file containing compressed masks from the segmentation algorithm
	# outputdirectory: directory to write images to
	# preprocessed_image_list: csv file containing list of images and their heights and widths'''

	print('Saving masks...')
	convert_to_image(predoutputfile, maskdir, imageinfooutputfile, cellminarea, rescale=False, scale_factor=2, verbose=False)
	print('Done.')

	# Count number of peroxisomes per cell using masks
	fileid = tail  # The name of the original processed image without the full path location

	# Function call to assign quantify POs per cell goes here
	quantify_POs_per_cell.quantify_and_save(thepath, maskdir, POdotcut, POminarea, cellminarea, maxintensity, "YeastSpotter", version)


for apath in paths:
	if os.path.isfile(apath):
		detect_cells(apath)
		gc.collect()

print("Done segmenting cells and computing peroxisome metrics for all imaging files.")
