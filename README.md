# perox-per-cell
Automated quantification of peroxisome characteristics in yeast cells based on fluorescence microscopy images


#### Table of Contents

- [SCOPE](#scope)
 - [PREREQUISITES](#prerequisites)
 - [RUNNING THE PROGRAM](#running-the-program)
   - [On Windows](#on-windows)
   - [On Mac OS X](#on-mac-os-x)
   - [On Linux](#on-linux)
 - [OUTPUT](#output)
 - [CONTACT](#contact)
 - [ATTRIBUTION](#attribution)
   - [Allen Institute Cell & Structure Segmenter](#allen-institute-cell--structure-segmenter)
   - [YeastSpotter](#yeastspotter)


## SCOPE
This program processes microscopy files to quantify the number of peroxisomes per yeast cell, cell and peroxisome areas, cytosolic peroxisomal signal intensities, as well as other features.
It expects the input file to include two channels: the first should contain fluoresence microscopy images of GFP-tagged peroxisomal markers in a Z-stack, the second channel should contain fluorescence images of the same Z-stack but captures whole cells stained with calcofluor white. 

While the software has primarily been tested using Zeiss Vision Image (.zvi) files, other imaging foramts such as TIFF files can also be used. Furthermore, Z-stacks are not required: 2D images can also be used for both channels. 

The program first generates intensity projections for both channels. Working from the resulting 2D images, the program then segments the peroxisomes using the Allen Cell and Structure Segmenter (https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based method called YeastSpotter (https://github.com/alexxijielu/yeast_segmentation). For each individual cell identified in the latter step, the program determines the number of unique peroxisome objects contained within that cell's boundary using output from the former step. It also computes the cell's physical area based on pixel resolution in the input file metadata as well as the total cytosolic (i.e., non-peroxisomal) signal present in the GFP channel. The program uses data from the maximal intensity projection of the GFP channel to quantify the latter signal. The program excludes cells that lie on the image border.

## PREREQUISITES
The program requires that you have Java installed on your machine.
If you need to install it, go to https://www.java.com/download/ie_manual.jsp.

The environment variable `JAVA_HOME` or `CP_JAVA_HOME` must also be set and must point to a valid Java installation so that the Bioformats package can be used to load imaging files.
If you need help setting the environment variable, [this page](https://www.wikihow.com/Set-Java-Home) may be helpful.

## RUNNING THE PROGRAM
Currently, the program processes one input file at a time. Mac and Linux users: Please keep all program files where they are in the downloaded repository. Otherwise, the program will likely fail to run.

### On Windows
1) Download and extract one of the perox-per-cell Windows executable package ZIPs under [Releases](https://github.com/AitchisonLab/perox-per-cell/releases).
2) Open the extracted perox_per_cell.bat file in a text editor and edit line 4 to provide the full path to the input imaging file you wish to process.
3) If needed, edit the values for parameters `POdotcut`, `POminarea`, and `POmaxintensity` in the .bat file.
    - `POdotcut` sets the sensitivity of peroxisome detection (lower is more sensitive)
    - `POminarea` sets the minimum size, in pixels, for a peroxisome to be counted
    - `POmaxintensity` should be set to one less than the maximum possible pixel intensity value for the input image. In other words, 2^(bit depth of input image) - 1
5) Save the edited perox_per_cell.bat file, then double-click it to execute the program. 
6) A command prompt window will appear and show messages output by the program. You may see many Java-related messages that can be ignored. When the program finishes, the window will close automatically. In initial tests, the program takes about 90 seconds to complete on a garden variety Windows desktop.
To keep the window containing the output messages from the program open after the program ends, you can also run the program from the command line by opening a command prompt, `cd`'ing to the directory containing the perox_per_cell.bat file and entering the command
`perox_per_cell.bat`

### On Mac OS X
Currently, a standalone executable for Mac OS X is not available. Installing the tool on Mac OS X requires some additional work to set up two conda environments that are then used to execute python files in the perox-per-cell repository.
Most of this will be done using commands entered in the Terminal app. Open it by going to _Applications > Utilities > Terminal_

1) Download all perox-per-cell repository files

   If downloading via the command line, you will need to have git-lfs installed, since some files in the repository are large. You can install git-lfs using homebrew:
   
   In a terminal window, enter the command:
   
   `brew install git-lfs`

   Confirm/initialize git-lfs by entering the command
   
   `git lfs install`

   Clone the perox-per-cell repository into the directory of your choice using these commands:
   
   `cd [path to directory]`

   `git-lfs clone https://github.com/AitchisonLab/perox-per-cell.git`

2) Ensure that Java is installed on your system and that the environment variable `JAVA_HOME` is set and points to a valid Java installation. You can check whether Java is installed by entering the command `java -version` in a terminal. If no version information is shown, Java is probably not installed. Download instructions are [here](https://www.java.com/en/download/apple.jsp)
   
    If Java is installed, you can set the `JAVA_HOME` environment variable for zsh (the default Mac OS shell) by entering the command
   
    `echo export "JAVA_HOME=\$(/usr/libexec/java_home)" >> ~/.zshrc`

    Bash shell users can set the variable using
   
    `echo export "JAVA_HOME=\$(/usr/libexec/java_home)" >> ~/.bash_profile`

    In either case, restart your shell after entering the command
   
 3) Next, ensure that conda is installed. Conda is a tool for managing virtual python environments. See [this website](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) for instructions on installing conda. Be sure to download the version that works for your processor (x86_64 or M1 Silicon)
 4) Using conda, set up two virtual python environments - one is used for segmenting peroxisomes, the other for cells.
    
    First, set up the environment for segmenting peroxisomes. Using the Terminal, `cd` to your downloaded perox-per-cell repository directory using the command
    
    `cd [path to downloaded repository]`
    
    Next, enter one of the following commands in a terminal to create the conda environment for peroxisome segmentation

    - For users with M1 Silicon processors (arm64 architecture): `CONDA_SUBDIR=osx-64 conda env create -f mac_environment_pseg.yml`

    - For users with x86_64 processors: `conda env create -f mac_environment_pseg.yml`
    
    Then, enter one of these commands to set up the cell segmenting environment (assuming the mac_environment_cseg.yml file is in the same directory as the other .yml file).
    
    - For users with M1 Silicon processors (arm64 architecture): `CONDA_SUBDIR=osx-64 conda env create -f mac_environment_cseg.yml`
    
    - For users with x86_64 processors: `conda env create -f mac_environment_cseg.yml`

 5) Open the perox-per-cell-macos.sh file in an editor and edit the line in the script that starts with “source” so that it points to your conda.sh file. (You only need to do this once, not each time you run the script.) If needed, you can get the directory containing the conda.sh file using the command.

    `conda info | grep -i 'base environment'`
     
    For example, if entering that command gives this output: `base environment : /opt/miniconda3 (writable)` then you would edit the line in the  perox-per-cell-macos.sh file to read
   
    `source /opt/miniconda3/etc/profile.d/conda.sh`

 6) Start using perox-per-cell

    Installation of the necessary files is complete and now the program can be executed.

    In the perox-per-cell-macos.sh file provided in the repository, enter the value for input parameter "file" (line 2 by default) so that it will process the desired image. For example

    `file="/Users/someuser/images/image1.zvi"`
     
    Make sure the other input parameters `POdotcut`, `POminarea`, and `POmaxintensity`, are set correctly for the analysis.
    - `POdotcut` sets the sensitivity of peroxisome detection (lower is more sensitive)
    - `POminarea` sets the minimum size, in pixels, for a peroxisome to be counted
    - `POmaxintensity` should be set to one less than the maximum possible pixel intensity value for the input image. In other words, `2^(bit depth of input image) - 1`
    
    In a Terminal, run the perox-per-cell program by `cd`’ing to its location, then entering the command
    `./perox-per-cell-macos.sh`

### On Linux
Currently, a standalone executable for Linux is not available, and the software has not yet been tested on Linux. However, the instructions above for running on Mac OS X may be helpful. Generally, the process of installing and running perox-per-cell on Linux will be similar.

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
### Allen Institute Cell & Structure Segmenter
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

### YeastSpotter

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
