#!/usr/bin/env python
# coding: utf-8
import sys
import numpy as np
import os

import cv2
import unidecode
import tkinter as tk
import json
import platform

from PIL import Image
from PIL.TiffTags import TAGS 
from tifffile import imread, imwrite, TiffFile
from typing import Union
from pathlib import Path
from skimage.morphology import remove_small_objects
from aicssegmentation.core.output_utils import (
    save_segmentation,
    generate_segmentation_contour
)
from aicssegmentation.core.pre_processing_utils import (
    intensity_normalization,
    image_smoothing_gaussian_slice_by_slice,
)
from aicssegmentation.core.seg_dot import dot_3d
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import Label
from tkinter import messagebox

try:
    import bioformats
    import javabridge
except:
    messagebox.showerror('Bioformats error', 'There was an issue loading the Java bridge and Bioformats.\n\n' +
                         'Please make sure Java is installed and the JAVA_HOME environment variable is set.\n\n' +
                         'Details about these program prerequisites are available in the README at https://github.com/AitchisonLab/perox-per-cell')
    sys.exit()


batchpath = sys.argv[1]
batchpath = os.path.join(batchpath, '')
print("Executable directory is " + batchpath)

# Function for opening the file dialog
def open_text_file():
    f = fd.askopenfile(initialdir=os.path.expanduser("~"))

    if f:  # If the string has some value (open file dialog wasn't cancelled)
        filetext.delete('1.0', 'end')
        filetext.insert('1.0', f.name)


# When the user hits the "Run" button, the job starts
def run_job():
    # Get path to image we are processing and the user-defined image processing parameters
    path = filetext.get("1.0", "end-1c")

    # Confirm that the entry in the filetext box is valid
    if not os.path.exists(path):
        messagebox.showerror('Error', 'Could not find file\n' + path + '\nPlease enter a valid file path.\n ')
        return

    # Collect image analysis parameters for job
    try:
        dot_3d_cutoff_par = float(senstext.get("1.0", "end-1c"))
        minarea_par = int(minpixtext.get("1.0", "end-1c"))
        maxintensity_par = int(bitstext.get("1.0", "end-1c"))
    except ValueError as ve:
        messagebox.showerror('Error', 'Invalid job parameter\n' + repr(ve))
        return

    # Hide the main GUI
    app.withdraw()

    # Start the Java VM for bioformats
    javabridge.start_vm(class_path=bioformats.JARS)
    # This is so that Javabridge doesn't spill out a lot of DEBUG messages during runtime.
    rootLoggerName = javabridge.get_static_field("org/slf4j/Logger", "ROOT_LOGGER_NAME", "Ljava/lang/String;")
    rootLogger = javabridge.static_call("org/slf4j/LoggerFactory", "getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
    logLevel = javabridge.get_static_field("ch/qos/logback/classic/Level", "WARN", "Lch/qos/logback/classic/Level;")
    javabridge.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)

    mypaths = javabridge.JClassWrapper('java.lang.System').getProperty('java.class.path').split(";")
    for mypath in mypaths:
        print("%s: %s" % ("exists" if os.path.isfile(mypath) else "missing", mypath))

    head, tail = os.path.split(path)

    # If we're processing all files in a directory, add them all to the queue
    if processdirvar.get() == 1:
        paths = []
        filenames = os.listdir(head)
        for f in filenames:
            paths.append(os.path.join(head, f))
    else:
        paths = [path]

    # Iterate through the imaging files to process
    subjobval = True
    filesnotprocessed = []
    for apath in paths:
        if os.path.isfile(os.path.join(head, apath)):
            subjobval = run_subjob(apath, dot_3d_cutoff_par, minarea_par, maxintensity_par)
            if not subjobval:
                filehead, filetail = os.path.split(apath)
                filesnotprocessed.append(filetail)  # Add path to list of paths we couldn't process (for warning message)
                print(apath + " could not be processed")

    if len(filesnotprocessed) > 0:  # Report files that couldn't be processed, if we're doing a batch
        badfiles = '\n'.join(filesnotprocessed)
        messagebox.showwarning('Warning', 'Some files could not be read.\n' + 'Please check that they are Bioformats-readable imaging files.\n\n' +
                                          badfiles + "\n\nPress OK to finish processing the job files that could be read.")

    if processdirvar.get() == 1 or subjobval:  # If we should write out configuration file
        # Write out configuration file, so it can be read by cell segmentation script
        configvals = {"Path": path,
                      'ProcessDir': processdirvar.get(),
                      'PeroxSensitivity': dot_3d_cutoff_par,
                      'MinPeroxArea': minarea_par,
                      'MaxIntensity': maxintensity_par}

        configloc = batchpath + 'ppc_job_config.json'

        with open(configloc, 'w') as configfile:
            configfile.write(json.dumps(configvals))

        app.destroy()  # Remove GUI
    else:
        app.deiconify()  # Un-hide the app so the user can configure a different job


def run_subjob(path="", dot_3d_cutoff_par=0.0064, minarea_par=1, maxintensity_par=16383):
    print("Peroxisome segmentation sensitivity parameter set to ", dot_3d_cutoff_par)
    print("Peroxisome minimum area in pixels set to ", minarea_par)
    print("Maximum possible intensity of image set to ", maxintensity_par)

    head, tail = os.path.split(path)

    # Load imaging file
    print("Loading " + path)

    # Get image metadata
    try:
        md = bioformats.get_omexml_metadata(path)
    except:
        return False

    md = bioformats.omexml.OMEXML(md)
    pixels = md.image(0).Pixels

    channel_count = pixels.SizeC
    stack_count = pixels.SizeZ
    timepoint_count = pixels.SizeT
    sizex = pixels.SizeX
    sizey = pixels.SizeY
    physsizexunit = pixels.PhysicalSizeXUnit
    physsizeyunit = pixels.PhysicalSizeYUnit
    physsizex = pixels.PhysicalSizeX
    physsizey = pixels.PhysicalSizeY
    pixarea = float(physsizex) * float(physsizey)

    print("Channel count: " + str(channel_count))
    print("Stack count: " + str(stack_count))
    print("Timepoint count: " + str(timepoint_count))
    print("Size of x: " + str(sizex))
    print("Size of y: " + str(sizey))
    print("Physical size of x: " + str(physsizex) + " " + physsizexunit)
    print("Physical size of y: " + str(physsizey) + " " + physsizeyunit)
    print(str(pixarea) + " " + physsizexunit + "^2 per pixel")

    struct_img_perox = np.empty([stack_count, sizey, sizex], np.uint16)  # ImageJ reads z,y,x
    struct_img_cells = np.empty([stack_count, sizey, sizex], np.uint16)

    rdr = bioformats.ImageReader(path, perform_init=True)

    # get peroxisome and cell images
    for z in range(stack_count):
        struct_img_perox[z, :, :] = rdr.read(z=z, t=0, c=0, rescale=False)  # c=0 for perox, c=1 for yeast
        struct_img_cells[z, :, :] = rdr.read(z=z, t=0, c=1, rescale=False)  # c=0 for perox, c=1 for yeast

    # Create maximum intensity Z-projection for peroxisome channel
    zperox = np.max(struct_img_perox, axis=0)

    # Create average intensity Z-projection for cell channel
    zcells = np.mean(struct_img_cells, axis=0)

    # Save out Z projections
    zprojdirperox = head + "/" + tail + "_Zprojections/perox/"
    zprojdircells = head + "/" + tail + "_Zprojections/cells/"

    if not os.path.exists(zprojdirperox):
        os.makedirs(zprojdirperox)
    if not os.path.exists(zprojdircells):
        os.makedirs(zprojdircells)

    peroxzpath = zprojdirperox + tail + "_peroxisome_Zprojection.tiff"
    cellszpath = zprojdircells + tail + "_cells_Zprojection.tiff"

    zperox_img = Image.fromarray(zperox)
    zcells_img = Image.fromarray(zcells)

    zperox_img.save(peroxzpath)
    zcells_img.save(cellszpath)

    # Use Allen Institute Segmenter to find peroxisomes first make output directory, if needed
    maskdir = head + "/" + tail + "_ZprojectionMasks/"
    if not os.path.exists(maskdir):
        os.makedirs(maskdir)

    # Put 2D maximum intensity projection for peroxisomes in a 3D array with one z-index
    temp_struct_img_perox = np.empty([1, sizey, sizex], np.uint16)
    temp_struct_img_perox[0, :, :] = zperox

    # Run Allen Institute Segmenter
    print("Segmenting peroxisomes...")
    Workflow_gja1(temp_struct_img_perox,
                  output_path=maskdir,
                  fn=tail + "_peroxisomes_",
                  dot_3d_cutoff=dot_3d_cutoff_par,
                  minarea=minarea_par,
                  maxintensity=maxintensity_par)
    print("Done.")

    # Load peroxisome mask to detect distinct objects
    peroxsegpath = maskdir + tail + "_peroxisomes__struct_segmentation.tiff"

    print("Identifying distinct peroxisomes in mask...")
    # From https://stackoverflow.com/questions/59150197/how-to-identify-distinct-objects-in-image-in-opencv-python
    # Load the image in grayscale
    input_image = cv2.imread(peroxsegpath, cv2.IMREAD_GRAYSCALE)

    # Threshold the image to make sure that is binary
    thresh_type = cv2.THRESH_BINARY + cv2.THRESH_OTSU
    _, binary_image = cv2.threshold(input_image, 0, 255, thresh_type)

    # Perform connected component labeling to give each distinct cell an ID
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=4)

    # Create false color image
    colors = np.random.randint(0, 255, size=(n_labels, 3), dtype=np.uint8)
    colors[0] = [0, 0, 0]  # for cosmetic reasons we want the background black
    false_colors = colors[labels]

    labelperoxpath = maskdir + tail + "_peroxisomes_labeled_objects.tiff"

    # Save labeled peroxisome image and store metadata about physical size of pixels in
    # ImageDescription tag which we will use later to compute cell area.
    unitalt = unidecode.unidecode(physsizexunit + "*" + physsizeyunit)

    imwrite(labelperoxpath, labels, description=str(pixarea) + " " + unitalt)

    print("Done.")
    print("Peroxisome intensity projections written to " + zprojdirperox)
    print("Cell intensity projections written to " + zprojdircells)
    print("Peroxisome masks written to " + os.path.abspath(maskdir))
    return True


# From gja1 (AKA Connexin-43?) workflow seen on napari and then downloaded code from
# https://github.com/AllenCell/aics-segmentation/blob/main/aicssegmentation/structure_wrapper/seg_gja1.py
def Workflow_gja1(
        struct_img: np.ndarray,
        rescale_ratio: float = -1,
        output_type: str = "default",
        output_path: Union[str, Path] = None,
        fn: Union[str, Path] = None,
        output_func=None,
        dot_3d_cutoff: float = 0.005,
        minarea: float = 1,
        maxintensity: float = 16383,
):
    # intensity_norm_param = [1, 999]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_3d_sigma = 1
    # dot_3d_cutoff = 0.005  # 0.025 # originally 0.031 but 0.01 found to be more sensitive for perox detection

    out_img_list = []
    out_name_list = []

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max) - This is performed in the original gja1 workflow,
    # but results in many false positive peroxisome detections for images without high-intensity
    # puncta. Instead of min/max normalization, we normalize to the maximum possible value
    # in the image.
    # struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)

    struct_img = struct_img / maxintensity  # Normalize to maximum theoretical intensity

    out_img_list.append(struct_img.copy())
    out_name_list.append("im_norm")

    # rescale if needed
    if rescale_ratio > 0:
        struct_img = zoom(struct_img, (1, rescale_ratio, rescale_ratio), order=2)

        struct_img = (struct_img - struct_img.min() + 1e-8) / (struct_img.max() - struct_img.min() + 1e-8)
        gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio

    # smoothing with gaussian filter
    structure_img_smooth = image_smoothing_gaussian_slice_by_slice(
        struct_img,
        sigma=gaussian_smoothing_sigma,
        truncate_range=gaussian_smoothing_truncate_range,
    )

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append("im_smooth")

    ###################
    # core algorithm
    ###################

    # step 1: LOG 3d
    response = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw = response > dot_3d_cutoff
    bw = remove_small_objects(bw > 0, min_size=minarea, connectivity=1, in_place=False)

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw, min_size=minarea, connectivity=1, in_place=False)

    # output
    seg = seg > 0
    seg = seg.astype(np.uint8)
    seg[seg > 0] = 255

    out_img_list.append(seg.copy())
    out_name_list.append("bw_final")

    if output_type == "default":
        # the default final output, simply save it to the output path
        save_segmentation(seg, False, Path(output_path), fn)
    elif output_type == "customize":
        # the hook for passing in a customized output function
        # use "out_img_list" and "out_name_list" in your hook to
        # customize your output functions
        output_func(out_img_list, out_name_list, Path(output_path), fn)
    elif output_type == "array":
        return seg
    elif output_type == "array_with_contour":
        return seg, generate_segmentation_contour(seg)
    else:
        raise NotImplementedError("invalid output type: {output_type}")


# Create the GUI
app = tk.Tk()
app.title('p e r o x - p e r - c e l l')

platform = platform.system()

if platform == "Darwin":
    app.geometry('675x275')  # Need some extra room on Mac
else:
    app.geometry('600x275')

# Create a textfield for inputting the file location
filetext = tk.Text(app, height=2, width=47)

# Add button for processing all files in a directory
processdirvar = tk.IntVar()
processdirbutton = tk.Checkbutton(app, text="Process all files in directory", variable=processdirvar, onvalue=1, offvalue=0)

# Create an open file button
open_button = ttk.Button(app, text='Select', command=open_text_file)
run_button = ttk.Button(app, text='Run', command=run_job, width=10)

# Peroxisome detection sensitivity
senstext = tk.Text(app, height=1, width=7)
senstext.insert('1.0', '0.0064')

# Minimum pixel size for peroxisomes
minpixtext = tk.Text(app, height=1, width=7)
minpixtext.insert('1.0', '1')

# Maximum signal intensity for peroxisome images
bitstext = tk.Text(app, height=1, width=7)
bitstext.insert('1.0', '16383')

# Specify the location of elements in GUI
Label(app, text="File to process").grid(row=0, column=0, padx=5, pady=10, sticky='nsew')
filetext.grid(column=1, row=0, columnspan=2, sticky='nsew', pady=10)
open_button.grid(column=3, row=0, sticky='nsew', padx=5, pady=10)
processdirbutton.grid(column=1, row=1, pady=0, sticky="w")
ttk.Separator(app, orient='horizontal').grid(column=0, row=2, columnspan=4, sticky='ew', pady=3, padx=3)

Label(app, text="Peroxisome detection sensitivity (lower is more sensitive)").grid(column=1, row=3, pady=10, padx=2, sticky='e')
senstext.grid(column=2, row=3, pady=10, padx=0)
Label(app, text="Minimum pixel count for peroxisomes").grid(column=1, row=4, pady=10, padx=2, sticky='e')
minpixtext.grid(column=2, row=4, pady=10, padx=0)
Label(app, text="Maximum intensity value in peroxisome channel (2^bit_depth – 1)").grid(column=1, row=5, pady=10, padx=2, sticky='e')
bitstext.grid(column=2, row=5, pady=10, padx=0)
ttk.Separator(app, orient='horizontal').grid(column=0, row=6, columnspan=4, sticky="ew", pady=3, padx=3)
run_button.grid(column=0, row=7, columnspan=4, pady=15)

# Make infinite loop for displaying app on the screen
print("\nperox-per-cell GUI ready.")
print("Please enter job configuration parameters and press \"Run\".")
app.mainloop()

# Be sure to kill the Java bridge before closing program
javabridge.kill_vm()
