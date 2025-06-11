# perox-per-cell
Automated quantification of peroxisome characteristics from fluorescence microscopy images.

[The peer-reviewed paper describing the software is available here.](https://doi.org/10.1093/bioinformatics/btae442.)
#### Citation:
Neal ML, Shukla N, Mast FD, Farré JC, Pacio TM, Raney-Plourde KE, Prasad S, Subramani S, Aitchison JD. Automated, image-based quantification of peroxisome characteristics with perox-per-cell. Bioinformatics. 2024 Jul 13;40(7):btae442.


## Table of Contents

- [SCOPE](#scope)
 - [PREREQUISITES](#prerequisites)
   - [Example Imaging Data](#example-imaging-data)
 - [RUNNING THE PROGRAM](#running-the-program)
   - [On Windows](#on-windows)
   - [On Mac OS X](#on-mac-os-x)
   - [On Linux](#on-linux)
 - [OUTPUT](#output)
 - [CONTACT](#contact)


## SCOPE
This program processes microscopy files to quantify the number of peroxisomes per yeast cell, cell and peroxisome areas, cytosolic peroxisomal signal intensities, as well as other features.
It expects the input file to include two channels: the first should contain fluoresence microscopy images of GFP-tagged peroxisomal markers in a Z-stack, the second channel should contain fluorescence images of the same Z-stack but capturing whole cells stained with calcofluor white. 

While the software has primarily been tested using Zeiss Vision Image (.zvi) files, other imaging formats such as TIFF files can also be used. Furthermore, Z-stacks are not required: 2D images can also be used for both channels. 

The program first generates intensity projections for both channels. Working from the resulting 2D images,it then segments peroxisomes using the [Allen Cell and Structure Segmenter](https://www.allencell.org/segmenter.html) and then segments whole cells using a neural network-based method named [YeastSpotter](https://github.com/alexxijielu/yeast_segmentation). For each individual cell identified in the latter step, the program determines the number of unique peroxisome objects contained within that cell's boundary using output from the former step. It also computes the cell's physical area based on pixel resolution in the input file metadata as well as the total cytosolic (i.e., non-peroxisomal) signal present in the GFP channel. The program uses data from the maximal intensity projection of the GFP channel to quantify the cytosolic signal. The program excludes cells that lie on the image border.

## PREREQUISITES
The program requires that you have Java installed.
If you need to install it, go to https://www.java.com/download/ie_manual.jsp.

The environment variable `JAVA_HOME` or `CP_JAVA_HOME` must also be set and must point to a valid Java installation so that the Bioformats package can be used to load imaging files.
If you need help setting the environment variable, [this page](https://www.wikihow.com/Set-Java-Home) may be helpful.

## Example Imaging Data
[An example input imaging file (ZVI format) capturing data from wild-type cells can be downloaded here](https://drive.google.com/file/d/1wJ4VLxBQHVSehQ41q6cxrtBX_huBt-Bj/view?usp=sharing). 

[A set of 44 imaging files (ZVI format) capturing data from various yeast strains with known peroxisomal defects can be downloaded here](https://doi.org/10.5281/zenodo.11375101).

## RUNNING THE PROGRAM
Please keep all program files where they are in the downloaded repository. Otherwise, the program will likely fail to run.

### On Windows
1) Download and extract one of the perox-per-cell Windows executable package ZIPs under [Releases](https://github.com/AitchisonLab/perox-per-cell/releases).
2) Double-click the extracted perox_per_cell.bat file. This will open a command prompt and the perox-per-cell GUI. It may take a few seconds to load.
3) Select an imaging file to process by pressing the "Select" button. You can choose to batch process all files in the image's folder by checking the "Process all files in directory" checkbutton.
4) If needed, edit the values for parameters in the GUI
    - The first sets the sensitivity of peroxisome detection (lower is more sensitive). Default is 0.0064.
    - The second sets the minimum size, in pixels, for a peroxisome to be counted. Default is 1.
    - The third should be set to one less than the maximum possible pixel intensity value for the input image. In other words, 2^(bit depth of input image) - 1. Default is 16383.
    - The fourth sets the cell segmentation method to use. Default is YeastSpotter (validated on images of yeast). The alternative is CellPose (validated on images of various cell types).
    - The fifth sets the minimum size, in pixels, for a segmented cell to be counted. Default is 1.
5) Press Run 
6) The GUI will close and messages output by the program will appear in the command prompt. You may see warning messages related to TensorFlow but they can be ignored. When the run finishes, the GUI will re-open and another run can be performed. In initial tests, the program takes less than 90 seconds to process one imaging file on a garden variety Windows desktop.

### On Mac OS X
Currently, a standalone executable for Mac OS X is not available. Installing the tool on Mac OS X requires setting up two conda environments that are then used to execute Python files in the perox-per-cell repository.

The software has not been extensively tested on Mac but the instructions below work for installation on an M1 Silicon machine running OS X 13.6.1, Java JDK 16.0.2 and conda 24.1.2.

We welcome feedback from the community to improve the software's performance on non-Windows machines.

Most of this will be done using commands entered in the Terminal app. Open it by going to _Applications > Utilities > Terminal_

1) Download perox-per-cell repository (via `git clone https://github.com/AitchisonLab/perox-per-cell.git`, etc.) and the yeast segmentation weights file

   The yeast segmentation weights file (~230 MB) is available [here](https://zenodo.org/record/3598690/files/weights.zip). Download the file so that it is in the main perox-per-cell directory, then unzip the file using 'unzip weights.zip`. This will unzip a folder called "weights" that contains the RCNN weights file deepretina_final.h5.

2) Ensure that Java is installed on your system and that the environment variable `JAVA_HOME` is set and points to a valid Java installation. You can check whether Java is installed by entering the command `java -version` in a terminal. If no version information is shown, Java is probably not installed. Download instructions are [here](https://www.java.com/en/download/apple.jsp).
   
    If Java is installed, you can set the `JAVA_HOME` environment variable for zsh (the default Mac OS shell) by entering the command
   
    `echo export "JAVA_HOME=\$(/usr/libexec/java_home)" >> ~/.zshrc`

    Bash shell users can set the variable using
   
    `echo export "JAVA_HOME=\$(/usr/libexec/java_home)" >> ~/.bash_profile`

    In either case, restart your shell after entering the command.
   
 3) Next, ensure that Conda is installed. Conda is a tool for managing virtual Python environments. See [this website](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) for instructions on installing conda. Be sure to download the version that works for your processor (x86_64 or M1 Silicon)
 4) Using Conda, set up two virtual Python environments - one is used for segmenting peroxisomes, the other for cells.
    
    First, set up the environment for segmenting peroxisomes. Using the Terminal, `cd` to your downloaded perox-per-cell repository directory using the command
    
    `cd [path to downloaded repository]`
    
    Next, enter one of the following commands in a terminal to create the Conda environment for peroxisome segmentation (this may take several minutes to complete because it will install a number of dependencies) 

    - For users with M1 Silicon processors (arm64 architecture): `CONDA_SUBDIR=osx-64 conda env create -f mac_environment_pseg.yml`

    - For users with x86_64 processors: `conda env create -f mac_environment_pseg.yml`
    
    Then, enter one of these commands to set up the cell segmenting environment (assuming the mac_environment_cseg.yml file is in the same directory as the other .yml file).
    
    - For users with M1 Silicon processors (arm64 architecture): `CONDA_SUBDIR=osx-64 conda env create -f mac_environment_cseg.yml`
    
    - For users with x86_64 processors: `conda env create -f mac_environment_cseg.yml`

 5) Open the perox_per_cell_macos.sh file in an editor and edit the line in the script that starts with “source” so that it points to your conda.sh file. (You only need to do this once, not each time you run the script.) If needed, you can get the directory containing the conda.sh file using the command.

    `conda info | grep -i 'base environment'`
     
    For example, if entering that command gives this output: `base environment : /opt/miniconda3 (writable)` then you would edit the line in the  perox-per-cell-macos.sh file to read
   
    `source /opt/miniconda3/etc/profile.d/conda.sh`

 6) Start using perox-per-cell

    Installation of the necessary files is complete and now the program can be executed.
    
    In a Terminal, run the perox-per-cell program by `cd`’ing to its location, then entering the command
    `./perox_per_cell_macos.sh`

    You may need to adjust the permissions on the file to make it executable, e.g., `chmod +x perox_per_cell_macos.sh`

### On Linux
Currently, a standalone executable for Linux is not available, but initial versions of the software have been successfully tested on a Windows Subsystem for Linux (WSL v1) running Ubuntu 22.04 using the steps below. These are generally similar to the installation/execution steps for Mac OS X (above). To summarize:

1) Download the perox-per-cell repository and the [RCNN weights file](https://zenodo.org/record/3598690/files/weights.zip)
2) Ensure Java is installed and the JAVA_HOME environment variable is set
3) Ensure that Conda is installed
4) Use the YAML files in the perox-per-cell repository to create the two Conda environments needed for segmenting peroxisomes and cells. Use the Linux-specific YAML files:
   - Enter this command to create the environment for segmenting peroxisomes: `conda env create -f linux_environment_pseg.yml`
   - Enter this command to create the environment for segmenting cells: `conda env create -f linux_environment_cseg.yml`
5) Edit the `perox_per_cell_linux.sh` file to ensure conda is sourced correctly on execution (see Mac OS X instructions for more details)
6) Execute the `perox_per_cell_linux.sh` file.

More details on each of these steps can be found in the Mac OS X installation/execution instructions above.

[An example input imaging file (ZVI format) capturing data from wild-type cells can be downloaded here](https://drive.google.com/file/d/1wJ4VLxBQHVSehQ41q6cxrtBX_huBt-Bj/view?usp=sharing).


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

Copyright &copy; 2023-2025

