~~~ perox-per-cell ~~~

A program for automatically quantifying the number of peroxisomes in yeast cells based on 
fluorescence microscopy images.

---------
| SCOPE |
---------
This program processes Zeiss Vision Image (.zvi) files to quantify the number of peroxisomes 
per yeast cell as well as cell area and cytosolic peroxisomal signal. It expects the .zvi file
to include two channels: the first should contain fluoresence microscopy images of GFP-tagged 
peroxisomal markers in a z-stack, the second channel should contain fluorescence images of the same
z-stack but captures whole cells stained with calcofluor white.

The program first generates intensity projections for both channels. Working from these
two images, the program then segments the peroxisomes using the Allen Cell and Structure Segmenter
(https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based 
method (https://github.com/alexxijielu/yeast_segmentation). For each individual cell
identified in the latter step, the program determines the number of unique peroxisome objects
contained within that cell's boundary using output from the former step. It also computes the cell's
physical area based on pixel resolution in the .zvi file metadata as well as the total cytosolic
(i.e., non-peroxisomal) signal present in the GFP channel. The program uses data from the maximal 
intensity projection of the GFP channel to quantify the latter signal. 
The program excludes cells that lie on the image border.

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
Currently, the program processes one .zvi file at a time. Please keep all files where they are
in the perox-per-cell program directory or else the program will probably break.

1) Open the perox_per_cell.bat file in a text editor and edit line 4 to provide the 
full path to the .zvi you wish to process.

2) Set the POdotcut (default=0.0064) and POminarea (default=1) parameters. The former controls the PO
detection sensitivity (lower is more sensitive) and the latter sets the minimum size (in pixels) 
threshold for peroxisomes

3) Save the edited perox_per_cell.bat file, then double-click it to run the program. 

4) A command prompt window will appear and show messages output by the program. When the 
program finishes, this window will close automatically. In initial tests, the program took
about 4 minutes to complete on a garden variety Windows desktop.

To keep the window containing the output messages from the program open after the program
ends, you can also run the program from the command line by opening a command prompt, cd'ing
to the directory containing the perox_per_cell.bat file and entering the command
perox_per_cell.bat

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

(c) 2023-2024

---------------
| ATTRIBUTION |
---------------

perox-per-cell uses YeastSpotter

YeastSpotter Mask R-CNN copyright (c) 2017 Matterport, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
