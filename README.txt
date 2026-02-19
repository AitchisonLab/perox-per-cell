~~~ feature-per-cell ~~~

Automated quantification of subcellular features on a cell-by-cell basis

---------
| SCOPE |
---------
This program processes microscopy files to quantify the number of subcellular features per cell, 
cell and feature areas, cytosolic feature signal intensities, as well as other characteristics. It
was originally designed to quantify the abundance and physical properties of peroxisomes within
yeast cells. The software expects the input imaging file to include two channels: the first should 
contain fluoresence microscopy images of GFP-tagged markers in a Z-stack, the second channel should 
contain fluorescence images of the same Z-stack but capturing whole cells.

While the software has primarily been tested using Zeiss Vision Image (.zvi) files, other imaging 
foramts such as TIFF files can also be used. Furthermore, Z-stacks are not required: 2D images 
can also be used for both channels.

The program first generates intensity projections for both channels. Working from the resulting 2D 
images, the program then segments the subcellular features using the Allen Cell and Structure Segmenter
(https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based 
method (https://github.com/alexxijielu/yeast_segmentation). For each individual cell identified in 
the latter step, the program determines the number of unique subcellular objects contained within 
that cell's boundary using output from the former step. It also computes the cell's physical area 
based on pixel resolution in the input file metadata as well as the total cytosolic 
(i.e., not within a segmented feature) signal present in the GFP channel. The program uses data from 
the maximal intensity projection of the GFP channel to quantify the latter signal. The program excludes
cells that lie on the image border.

-----------------
| PREREQUISITES |
-----------------
The program requires that you have Java installed on your machine.
If you need to install it, go to https://www.java.com/download/ie_manual.jsp

The environment variable JAVA_HOME or CP_JAVA_HOME also must be set so that
the bioformats package can use java to load in the raw image file.

-----------------------
| RUNNING THE PROGRAM |
-----------------------
Please keep all files where they are in the feature-per-cell program directory or else the program 
will likely break.

1) Download and extract one of the feature-per-cell Windows executable package ZIPs under Releases
on the feature-per-cell GitHub site: https://github.com/AitchisonLab/feature-per-cell/releases

2) Double-click the extracted feature_per_cell.bat file. This will open a command prompt and the 
feature-per-cell GUI.

3) Select an imaging file to process by pressing the "Select" button. You can choose to batch process 
all files in the directory by checking the "Process all files in directory" box.

4) If needed, edit the values for parameters in the GUI
	- The first sets the sensitivity of subcellular feature detection (lower is more sensitive). 
	    Default is 0.0064.
	- The second sets the minimum size, in pixels, for a segmented subcellular feature to be counted. 
	    Default is 1.
	- The third should be set to one less than the maximum possible pixel intensity value for the input 
	    image. In other words, 2^(bit depth of input image) - 1. Default is 16383.
	- The fourth sets the cell segmentation method to use. Default is YeastSpotter (validated on images 
	    of yeast). The alternative is CellPose (validated on images of various cell types).
	- The fifth sets the minimum size, in pixels, for a segmented cell to be counted. Default is 1.

5) Press Run

6) The GUI will close and messages output by the program will appear in the command prompt. When the run 
finishes, the GUI will re-open and another run can be performed. In initial tests, the program takes less 
than 90 seconds to process one imaging file on a garden variety Windows desktop.

Please see instructions on the feature-per-cell GitHub site for running on Mac and Linux machines:
https://github.com/AitchisonLab/feature-per-cell/blob/main/README.md#on-mac-os-x
https://github.com/AitchisonLab/feature-per-cell/blob/main/README.md#on-linux

----------
| OUTPUT |
----------
The program outputs an Excel spreadsheet in the same directory as the .zvi file. The spreadsheet
contains three worksheets:

ByCell: lists each unique cell, the number of subcellular features it contains, its area, the cumulative
              area of all subcellular features in the cell and feature marker signal intensities 
			  (total and cytosolic).

ByPeroxisome: lists each unique subcellular feature's area and signal intensity as well as metrics for the
              cell that contained it (some are repeated in the "ByCell" worksheet)
			  
OtherStats: lists other statistics that may be useful such as the number of subcellular features detected
            outside of cell boundaries (high values may indicate inaccurate cell segmentation). Also stores
			the software version ID.
			  
The program also stores the intensity projection files and the segmentation masks in folders
contained in the same directory as the .zvi file.

-----------
| CONTACT |
-----------
max.neal@seattlechildrens.org
Aitchison Lab
Center for Global Infectious Disease Research
Seattle Children's Research Institute

(c) 2023-2026
