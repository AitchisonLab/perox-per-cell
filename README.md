# perox-per-cell
Automated quantification of peroxisome characteristics in yeast cells based on fluorescence microscopy images



## SCOPE
This program processes microscopy files to quantify the number of peroxisomes per yeast cell, cell and peroxisome areas, cytosolic peroxisomal signal intensities, as well as other features.
It expects the input file to include two channels: the first should contain fluoresence microscopy images of GFP-tagged peroxisomal markers in a Z-stack, the second channel should contain fluorescence images of the same Z-stack but captures whole cells stained with calcofluor white. Note that while the software has primarily been tested using Zeiss Vision Image (.zvi) files, other imaging foramts such as TIFF files can also be used. Furthermore, Z-stacks are not required: 2D images can also be used for both channels. 

The program first generates intensity projections for both channels. Working from the resulting 2D images, the program then segments the peroxisomes using the Allen Cell and Structure Segmenter (https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based method called YeastSpotter (https://github.com/alexxijielu/yeast_segmentation). For each individual cell identified in the latter step, the program determines the number of unique peroxisome objects contained within that cell's boundary using output from the former step. It also computes the cell's physical area based on pixel resolution in the input file metadata as well as the total cytosolic (i.e., non-peroxisomal) signal present in the GFP channel. The program uses data from the maximal intensity projection of the GFP channel to quantify the latter signal. The program excludes cells that lie on the image border.

## PREREQUISITES
The program requires that you have Java installed on your machine.
If you need to install it, go to https://www.java.com/download/ie_manual.jsp

The environment variable JAVA_HOME or CP_JAVA_HOME must also be set and must point to a valid java installation so that the bioformats package can use java to load in the raw image file.

## RUNNING THE PROGRAM
Currently, the program processes one input file at a time. Please keep all program files where they are in the perox-per-cell directory. Otherwise, the program will likely fail to run.

### On Windows
1) Download one of the perox-per-cell Windows executable ZIPs under "Releases"
2) Extract files in the downloaded ZIP
3) Open the extracted perox_per_cell.bat file in a text editor and edit line 4 to provide the full path to the input file you wish to process.
4) Set the `POdotcut` and `POminarea` parameters in the .bat file. The former controls the peroxisome detection sensitivity (lower is more sensitive) and the latter sets the minimum size threshold for peroxisomes (in pixels).
5) Save the edited perox_per_cell.bat file, then double-click it to run the program. 
6) A command prompt window will appear and show messages output by the program. When the program finishes, this window will close automatically. In initial tests, the program takes about 90 seconds to complete on a garden variety Windows desktop.
To keep the window containing the output messages from the program open after the program ends, you can also run the program from the command line by opening a command prompt, `cd`'ing to the directory containing the perox_per_cell.bat file and entering the command
`perox_per_cell.bat`

### On Mac OS X
_(TBA)_

## OUTPUT
The program outputs an Excel spreadsheet in the same directory as the input imaging file. The spreadsheet contains three worksheets:

- **ByCell**: lists each unique cell, the number of peroxisomes it contains, its area, the cumulative area of all peroxisomes in the cell and peroxisomal marker signal intensities (total and cytosolic).

- **ByPeroxisome**: lists each unique peroxisome's area and signal intensity as well as metrics for the cell that contained it (some are repeated in the "ByCell" worksheet)
			  
- **OtherStats**: lists other statistics that may be useful such as the number of peroxisomes detected outside of cell boundaries. Also stores the software version ID.
			  
The program also stores the intensity projection files and the segmentation masks in folders contained in the same directory as the input imaging file.

## CONTACT
max[dot]neal[at]seattlechildrens[dot]org

Aitchison Lab

Center for Global Infectious Disease Research

Seattle Children's Research Institute

Copyright &copy; 2023-2024

## ATTRIBUTION
### perox-per-cell uses the Allen Institute Cell & Structure Segmenter
Allen Institute Software License – This software license is the 2-clause BSD
license plus a third clause that prohibits redistribution and use for
commercial purposes without further permission.

Copyright © 2020
Jianxu Chen, Allen Institute.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Redistributions and use for commercial purposes are not permitted without
the Allen Institute’s written permission. For purposes of this license,
commercial purposes are the incorporation of the Allen Institute's software
into anything for which you will charge fees or other compensation or use of
the software to perform a commercial service for a third party. Contact
terms@alleninstitute.org for commercial licensing opportunities.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### perox-per-cell uses YeastSpotter

YeastSpotter Mask R-CNN copyright &copy; 2017 Matterport, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
