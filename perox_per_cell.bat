@echo off 

:: Path to imaging file to process
set file="Y:\mneal\Peroxisomes_MastR01\ImageQuantification\perox_per_cell_validation\Compute signal of cytosolic reporter per cell\BY4742-pLT1-T1_25C_region1_500ms.zvi"

:: Parameter that changes the sensitivity of peroxisome detection (lower for more sensitive detection)
set POdotcut=0.0064

:: Parameter that sets the minimum area (in pixels) for a peroxisome
set POminarea=1

:: Parameter that indicates the maximum intensity value possible in peroxisome channel images ( 2^(bit depth) - 1)
set POmaxintensity=16383


:: if the ZVI file doesn't exist, show error message and close.
if exist %file% (
 goto RUN
) else (
 goto FILENOTFOUNDERROR
)

:FILENOTFOUNDERROR
echo ERROR: Could not find imaging file %file%
echo Please make sure the path to the file is entered correctly in the .bat script
pause
goto END

:RUN
echo Running perox_per_cell on %file%

:: Set output directory for z-projections and masks
set zprojdircells=%file%_Zprojections\cells\
set zprojmasksdir=%file%_ZprojectionMasks\

:: Run the file that makes the z-projections and the peroxisome masks
dist\zproject_get_perox_masks.exe %file% %POdotcut% %POminarea% %POmaxintensity%
echo Finished segmenting peroxisomes. Segmenting cells and computing peroxisomes per cell.

::Get cell masks and count peroxisomes per cell
dist\get_cell_masks_and_count.exe %file% %zprojdircells% %zprojmasksdir% %POdotcut% %POminarea% %POmaxintensity%

:END
