~~~ perox-per-cell ~~~

Automated quantification of peroxisome characteristics in yeast cells

---------
| SCOPE |
---------
This program processes microscopy files to quantify the number of peroxisomes per yeast cell, 
cell and peroxisome areas, cytosolic peroxisomal signal intensities, as well as other features. 
It expects the input file to include two channels: the first should contain fluoresence microscopy 
images of GFP-tagged peroxisomal markers in a Z-stack, the second channel should contain 
fluorescence images of the same Z-stack but capturing whole cells stained with calcofluor white.

While the software has primarily been tested using Zeiss Vision Image (.zvi) files, other imaging 
foramts such as TIFF files can also be used. Furthermore, Z-stacks are not required: 2D images 
can also be used for both channels.

The program first generates intensity projections for both channels. Working from the resulting 2D 
images, the program then segments the peroxisomes using the Allen Cell and Structure Segmenter
(https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based 
method (https://github.com/alexxijielu/yeast_segmentation). For each individual cell identified in 
the latter step, the program determines the number of unique peroxisome objects contained within 
that cell's boundary using output from the former step. It also computes the cell's physical area 
based on pixel resolution in the input file metadata as well as the total cytosolic 
(i.e., non-peroxisomal) signal present in the GFP channel. The program uses data from the maximal 
intensity projection of the GFP channel to quantify the latter signal. The program excludes cells 
that lie on the image border.

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
Please keep all files where they are in the perox-per-cell program directory or else the program 
will probably break.

1) Download and extract one of the perox-per-cell Windows executable package ZIPs under Releases
on the perox-per-cell GitHub site: https://github.com/AitchisonLab/perox-per-cell/releases

2) Double-click the extracted perox_per_cell.bat file. This will open a command prompt and the 
perox-per-cell GUI.

3) Select an imaging file to process by pressing the "Select" button. You can choose to batch process 
all files in the directory by checking the "Process all files in directory" checkbutton.

4) If needed, edit the values for parameters in the GUI
	- The first sets the sensitivity of peroxisome detection (lower is more sensitive). Default is 0.0064.
	- The second sets the minimum size, in pixels, for a peroxisome to be counted. Default is 1.
	- The third should be set to one less than the maximum possible pixel intensity value for the input image.
    	In other words, 2^(bit depth of input image) - 1. Default is 16383.
		
5) Press Run

6) The GUI will close and messages output by the program will appear in the command prompt. When the run 
finishes, the GUI will re-open and another run can be performed. In initial tests, the program takes less 
than 90 seconds to process one imaging file on a garden variety Windows desktop.

Please see instructions on the perox-per-cell GitHub site for running on Mac and Linux machines:
https://github.com/AitchisonLab/perox-per-cell/blob/main/README.md#on-mac-os-x
https://github.com/AitchisonLab/perox-per-cell/blob/main/README.md#on-linux

----------
| OUTPUT |
----------
The program outputs an Excel spreadsheet in the same directory as the .zvi file. The spreadsheet
contains three worksheets:

ByCell: lists each unique cell, the number of peroxisomes it contains, its area, the cumulative area
              of all peroxisomes in the cell and peroxisomal marker signal intensities 
			  (total and cytosolic).

ByPeroxisome: lists each unique peroxisome's area and signal intensity as well as metrics for the cell
              that contained it (some are repeated in the "ByCell" worksheet)
			  
OtherStats: lists other statistics that may be useful such as the number of peroxisomes detected
            outside of cell boundaries. Also stores the software version ID.
			  
The program also stores the intensity projection files and the segmentation masks in folders
contained in the same directory as the .zvi file.

-----------
| CONTACT |
-----------
max.neal@seattlechildrens.org
Aitchison Lab
Center for Global Infectious Disease Research
Seattle Children's Research Institute

(c) 2023-2025
