@echo off 
echo Loading perox-per-cell...

: START
:: Run the file that makes the z-projections, segments peroxisomes, and runs CellPose segmentation (if requested)
dist\zproject_get_perox_masks.exe "%~dp0\"

set "configfile=%~dp0ppc_job_config.json"

:: If job configuration file has been written out, perform cell segmentation with YeastSpotter and peroxisome counting
if exist "%configfile%" (
  echo Segmenting cells and computing peroxisomes per cell
  dist\get_cell_masks_YS_and_count.exe "%configfile%"
)

if exist "%configfile%" (
  del "%configfile%"
  :: Re-open GUI for additional jobs
  goto START
) else (
  :: If no configuration file, no job was run. Close.
  goto END
)

: END
