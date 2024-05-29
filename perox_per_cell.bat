@echo off 
echo Starting perox-per-cell...
: START
:: Run the file that makes the z-projections and the peroxisome masks
dist\zproject_get_perox_masks.exe %~dp0

set configfile=%~dp0\ppc_job_config.json

:: If job configuration file has been written out, perform cell segmentation and peroxisome counting
if exist %configfile% (
  echo Segmenting cells and computing peroxisomes per cell
  dist\get_cell_masks_and_count.exe %configfile%
)

if exist %configfile% (
  del %configfile%
  :: Re-open GUI for additional jobs
  goto START
) else (
  :: If no configuration file, no job was run. Close.
  goto END
)

: END



:: @echo off 

:: echo %0
:: echo %~dp0
:: echo %~f0
:: Path to imaging file to process
:: set file="Y:\mneal\Peroxisomes_MastR01\ImageQuantification\testImages\39_zstack.zvi"

:: Parameter that changes the sensitivity of peroxisome detection (lower for more sensitive detection)
:: set POdotcut=0.0064

:: Parameter that sets the minimum area (in pixels) for a peroxisome
:: set POminarea=1

:: Parameter that indicates the maximum intensity value possible in peroxisome channel images ( 2^(bit depth) - 1)
:: set POmaxintensity=16383


:: if the ZVI file doesn't exist, show error message and close.
:: if exist %file% (
::  goto RUN
:: ) else (
::  goto FILENOTFOUNDERROR
:: )

:: :FILENOTFOUNDERROR
:: echo ERROR: Could not find imaging file %file%
:: echo Please make sure the path to the file is entered correctly in the .bat script
:: pause
:: goto END

:: :RUN
:: echo Running perox_per_cell on %file%

:: Set output directory for z-projections and masks
:: set zprojdircells=%file%_Zprojections\cells\
:: set zprojmasksdir=%file%_ZprojectionMasks\

:: Run the file that makes the z-projections and the peroxisome masks
:: dist\zproject_get_perox_masks.exe %file% %POdotcut% %POminarea% %POmaxintensity%
:: dist\zproject_get_perox_masks.exe
:: echo Finished segmenting peroxisomes. Segmenting cells and computing peroxisomes per cell.

::Get cell masks and count peroxisomes per cell
:: dist\get_cell_masks_and_count.exe %file% %zprojdircells% %zprojmasksdir% %POdotcut% %POminarea% %POmaxintensity%
:: dist\get_cell_masks_and_count.exe

:::END
