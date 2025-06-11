import os
import numpy as np
import pandas as pd
import random

from tifffile import imread, TiffFile


# Function to set column widths of worksheets in output Excel file
def set_column_widths(theworksheet, thedf, width):
    for theidx, thecol in enumerate(thedf):  # loop through all columns
        theworksheet.set_column(theidx, theidx, width)  # set column width


# sourceimagepath: full path to original source image to process
# maskdir: output directory for peroxisome and cell masks
# POdotcut: Peroxisome segmentation sensitivity parameter
# POminarea: Minimum area for peroxisomes
# cellminarea: Minimum area for cells
# maxintensity: Theoretical maximum intensity level of input images
# version: Software version
def quantify_and_save(sourceimagepath, maskdir, POdotcut, POminarea, cellminarea, maxintensity, cellsegmenter, version):

    head, tail = os.path.split(sourceimagepath)
    fileid = tail

    # Get masks and count number of peroxisomes per cell
    print("Counting peroxisomes per cell for " + fileid)
    cells = maskdir + os.path.splitext(fileid)[0] + '.tif'  # Segmented cells mask
    perox = maskdir + fileid + '_peroxisomes_labeled_objects.tiff'  # Segmented peroxisomes mask
    rawzprojperox = sourceimagepath + '_Zprojections/perox/' + fileid + '_peroxisome_Zprojection.tiff'

    cellseg = imread(cells)
    peroxseg = imread(perox)
    peroxrawz = imread(rawzprojperox)

    # Collect pixel physical area stored in labeled peroxisome image
    frames = TiffFile(perox)
    page = frames.pages[0]
    idesc = page.tags[
        "ImageDescription"].value  # area per pixel followed by a space then the physical units for the area
    tokens = idesc.split()
    pixarea = tokens[0]
    pixareaunits = tokens[1]

    print("Pixel area: " + pixarea)
    print("Pixel area units: " + pixareaunits)

    # Collect cells on the image border so we can omit them from analysis
    edgecells = []
    edgecells.extend(np.unique(cellseg[0, :]))  # top edge
    edgecells.extend(np.unique(cellseg[:, 0]))  # left edge
    edgecells.extend(np.unique(cellseg[(cellseg.shape[0] - 1), :]))  # bottom edge
    edgecells.extend(np.unique(cellseg[:, (cellseg.shape[1] - 1)]))  # right edge
    edgecells = np.unique(edgecells).tolist()  # unique IDs for cells on image border
    edgecells.remove(0)  # remove 0 value

    image_id = []
    cell_id = []
    num_per = []
    cell_area = []
    cytoPOsignal = []
    totalPOsignal = []
    totalPOarea = []
    POsAssignedToOtherCellsSignal = []

    # Set up similar arrays for the excel sheet that lists all peroxisomes
    image_id_PO = []
    cell_id_PO = []
    num_per_PO = []
    cell_area_PO = []
    cytoPOsignal_PO = []
    totalPOsignal_PO = []
    perox_id_PO = []
    perox_area_PO = []
    perox_area_in_cell_PO = []
    perox_signal_PO = []
    perox_signal_in_cell_PO = []

    maxcellid = 0
    print("Num cell ids: " + str(len(np.unique(cellseg[cellseg > 0]))))
    if len(np.unique(cellseg[cellseg > 0])) > 0:
        cellids = [i for i in np.unique(cellseg) if i > 0]
        maxcellid = np.max(cellids)
    else:
        cellids = []

    maxperoxid = 0
    print("Num perox ids: " + str(len(np.unique(peroxseg[peroxseg > 0]))))
    if len(np.unique(peroxseg[peroxseg > 0])) > 0:
        peroxids = [j for j in np.unique(peroxseg) if j > 0]
        maxperoxid = np.max(peroxids)
    else:
        peroxids = []

    peroxidsnotincells = peroxids.copy()

    # Populate arrays that record the overlap between cells and peroxisomes
    # as well as the signal intensity in those overlapping regions
    # This ensures that each peroxisome is assigned to only one cell

    POcellArrayOverlap = np.zeros((int(maxperoxid) + 1, int(maxcellid) + 1), dtype=np.float)  # Initialize
    POcellArrayIntensity = np.zeros((int(maxperoxid) + 1, int(maxcellid) + 1), dtype=np.float)  # Initialize

    print("Assigning peroxisomes to cells")
    for i in cellids:
        cellmask = cellseg.copy()
        cellmask[cellseg != i] = 0
        cellmask[cellmask > 0] = 1

        # Get peroxisomes inside cell boundary (even if cell is on edge), exclude 0 values
        peroxsegmaskincell = peroxseg * cellmask  # only includes segmented peroxisomes within cell
        peroxidsincell = [k for k in np.unique(peroxsegmaskincell) if k > 0]

        # Record number of overlapping pixels and summed intensity within cell for each peroxisome that overlaps with cell
        for p in peroxidsincell:
            peroxsegmaskincellcopy = peroxsegmaskincell.copy()
            peroxsegmaskincellcopy[peroxsegmaskincellcopy != p] = 0
            peroxsegmaskincellcopy[peroxsegmaskincellcopy > 0] = 1
            POoverlapVal = np.sum(peroxsegmaskincellcopy)

            peroxrawonePO = peroxsegmaskincellcopy * peroxrawz
            POintensityVal = np.sum(peroxrawonePO)

            # Check if this same peroxisome has already been assigned a cell
            POoverlaps = POcellArrayOverlap[int(p)]
            alreadyassigned = len(POoverlaps[POoverlaps != 0]) > 0

            if alreadyassigned:
                assignPOtocell = False
                # Compare num. overlapping pixels
                maxexistingoverlap = max(
                    POcellArrayOverlap[int(p)])  # Maximum value in row representing overlaps with cells
                existingcellindex = np.argmax(POcellArrayOverlap[int(p)])  # Index of maximum value

                if maxexistingoverlap > POoverlapVal:
                    continue  # Skip this peroxisome because it should be assigned to a different cell
                elif maxexistingoverlap < POoverlapVal:
                    assignPOtocell = True
                else:  # If the peroxisome's area is equally shared among cells...
                    # Compare the summed intensity values
                    maxexistingintensity = max(POcellArrayIntensity[int(p)])

                    if maxexistingintensity > POintensityVal:
                        continue  # Skip this peroxisome because it should be assigned to a different cell
                    elif maxexistingintensity < POintensityVal:
                        assignPOtocell = True
                    else:  # If the peroxisome's area is perfectly split between multiple cells as well as its signal...
                        # Coin flip to decide whether to assign PO to cell or keep the existing assignment
                        assignPOtocell = random.choice([True, False])

                if assignPOtocell:
                    # Replace the existing overlap and intensity values with zeros
                    POcellArrayOverlap[int(p)][existingcellindex] = 0
                    POcellArrayIntensity[int(p)][existingcellindex] = 0

            # If we're here it means we should assign the peroxisome to the cell
            POcellArrayOverlap[int(p)][int(i)] = POoverlapVal  # Record n pixels overlapping
            POcellArrayIntensity[int(p)][int(i)] = POintensityVal  # Record summed intensity of overlapping pixels

    # For each cell, collect metrics
    for i in cellids:
        # Get num peroxisomes and other metrics for the current cell
        cellmask = cellseg.copy()
        cellmask[cellseg != i] = 0
        cellmask[cellmask > 0] = 1

        # Get peroxisomes assigned to cell boundary (even if cell is on edge), exclude 0 values
        peroxidsincell = np.argwhere(POcellArrayOverlap[:, int(i)] != 0)
        peroxidsnotincells = np.setdiff1d(peroxidsnotincells, peroxidsincell)

        if i in edgecells:  # skip if it's a cell on the image border
            continue

        if (i % 10) == 0:  # report progress
            print("Finished ", str(int(i)), " of ", str(int(np.max(cellids))), " cells")

        npixels = np.sum(cellmask)
        carea = float(pixarea) * float(npixels)  # cell area
        per = peroxseg * cellmask  # only includes segmented POs within cell (can include POs assigned to other cells)
        per_num = len(peroxidsincell)  # get number of unique peroxisomes in cell. minus one to remove 0 value
        image_id.append(fileid)
        cell_id.append(i)
        num_per.append(per_num)
        cell_area.append(carea)

        # Get cytosolic peroxisomal signal within the cell using the maximum Z-projection of the
        # original peroxisome image
        singlecellrawperox = peroxrawz * cellmask  # exclude all signal not within cell boundary
        singlecellrawperoxtot = singlecellrawperox.copy()
        totalPOsignalval = np.sum(singlecellrawperoxtot)
        totalPOsignal.append(totalPOsignalval)
        singlecellrawperox[per != 0] = 0  # Remove segmented peroxisomes from raw signal
        cytoPOsignalval = np.sum(singlecellrawperox)
        cytoPOsignal.append(cytoPOsignalval)

        # Add in total peroxisomal area in cell
        perbinary = per.copy()
        perbinary[perbinary > 0] = 1
        nperoxpixels = np.sum(perbinary)
        totalPOareaval = float(pixarea) * float(nperoxpixels)
        totalPOarea.append(totalPOareaval)

        # Collect the signal from POs that overlap with this cell but were assigned to other cells
        # because they overlapped more with other cells or were split evenly but had a higher signal
        # in other cells (or were randomly assigned to other cells).
        # First get signal from all segmented POs within cell bounds
        peroxsegassignedothers = per

        for k in peroxidsincell:  # k values are ints
            # signal from segmented POs within cell bounds that were assigned to other cells
            peroxsegassignedothers[peroxsegassignedothers == k] = 0

        peroxsegassignedothers[peroxsegassignedothers > 0] = 1  # Make binary
        singlecellrawperoxotherassign = singlecellrawperoxtot * peroxsegassignedothers
        POsAssignedToOtherCellsSignal.append(np.sum(singlecellrawperoxotherassign))

        # For each peroxisome assigned to the cell, collect metrics
        for p in peroxidsincell:
            image_id_PO.append(fileid)
            cell_id_PO.append(i)
            num_per_PO.append(per_num)
            cell_area_PO.append(carea)
            cytoPOsignal_PO.append(cytoPOsignalval)
            totalPOsignal_PO.append(totalPOsignalval)
            perox_id_PO.append(int(p))

            peroxsegmask = peroxseg.copy()  # Includes all of the peroxisome, even if outside of cell bounds
            peroxsegmask[peroxsegmask != p] = 0
            peroxsegmask[peroxsegmask > 0] = 1
            npixels_PO = np.sum(peroxsegmask)
            parea = float(pixarea) * float(npixels_PO)  # complete perox area, including pixels outside of cell
            perox_area_PO.append(parea)

            npixels_in_cell_PO = POcellArrayOverlap[int(p)][int(i)]
            pareaincell = float(pixarea) * float(npixels_in_cell_PO)  # perox area that is inside the cell
            perox_area_in_cell_PO.append(pareaincell)

            # Add in total intensity for individual PO (this includes the full segmented PO, not just the part in the cell)
            singleperoxraw = peroxrawz * peroxsegmask  # exclude all signal not within perox
            singleperoxsignal = np.sum(singleperoxraw)
            perox_signal_PO.append(singleperoxsignal)

            # Collect the intensity of the part of the PO that was in the cell (usually the same as the full PO)
            singleperoxsignalincell = POcellArrayIntensity[int(p)][int(i)]
            perox_signal_in_cell_PO.append(singleperoxsignalincell)

    # Format data frame for "ByCell" sheet
    df = pd.DataFrame({'image ID': image_id, 'cell ID': cell_id, 'num peroxisomes in cell': num_per,
                       'cell area': cell_area, 'total peroxisome area in cell': totalPOarea,
                       'total perox channel signal': totalPOsignal,
                       'cytosolic perox signal': cytoPOsignal,
                       'signal from peroxisomes assigned to other cells': POsAssignedToOtherCellsSignal})
    areacolname = 'cell area (' + pixareaunits + ')'
    peroxareacolname = 'total peroxisome area in cell (' + pixareaunits + ')'
    df.rename(columns={'cell area': areacolname}, inplace=True)
    df.rename(columns={'total peroxisome area in cell': peroxareacolname}, inplace=True)

    # Format data frame for "ByPeroxisome" sheet
    df_PO = pd.DataFrame({'image ID': image_id_PO,
                          'cell ID': cell_id_PO,
                          'num peroxisomes in cell': num_per_PO,
                          'cell area': cell_area_PO,
                          'total perox channel signal': totalPOsignal_PO,
                          'cytosolic perox signal': cytoPOsignal_PO,
                          'peroxisome ID': perox_id_PO,
                          'peroxisome area': perox_area_PO,
                          'peroxisome area in cell': perox_area_in_cell_PO,
                          'peroxisome signal': perox_signal_PO,
                          'peroxisome signal in cell': perox_signal_in_cell_PO})
    df_PO.rename(columns={'cell area': areacolname}, inplace=True)
    areacolname_PO = 'peroxisome area (' + pixareaunits + ')'
    df_PO.rename(columns={'peroxisome area': areacolname_PO}, inplace=True)
    areacolnameinonly_PO = 'peroxisome area in cell (' + pixareaunits + ')'
    df_PO.rename(columns={'peroxisome area in cell': areacolnameinonly_PO}, inplace=True)

    # Other stats
    properties = []
    values = []

    peroxoutsideval = len(peroxidsnotincells)
    properties.append("N peroxisomes outside cells")
    values.append(peroxoutsideval)

    peroxoutsidefracval = "N/A"

    if len(peroxids) > 0:
        peroxoutsidefracval = float(peroxoutsideval) / float(len(peroxids))

    properties.append("Fraction of peroxisomes outside cells")
    values.append(peroxoutsidefracval)

    properties.append("File processed")
    values.append(sourceimagepath.replace('\\', '/'))  # Sometimes there is a mix of / and \ in file path (?)

    properties.append("POdotcut")
    values.append(POdotcut)

    properties.append("POminarea")
    values.append(POminarea)

    properties.append("cellminarea")
    values.append(cellminarea)

    properties.append("maxintensity")
    values.append(maxintensity)

    properties.append("CellSegmenter")
    values.append(cellsegmenter)

    properties.append("perox-per-cell version")
    values.append(version)

    df_OS = pd.DataFrame({'Property': properties, 'Value': values})

    with pd.ExcelWriter(head + '/' + fileid + '_perox_per_cell.xlsx') as writer:

        df.to_excel(writer, sheet_name='ByCell',
                    columns=["image ID", "cell ID", "num peroxisomes in cell", areacolname, peroxareacolname,
                             "total perox channel signal", "cytosolic perox signal",
                             "signal from peroxisomes assigned to other cells"], index=False)
        set_column_widths(writer.sheets['ByCell'], df, 33)  # set column widths

        df_PO.to_excel(writer, sheet_name='ByPeroxisome',
                       columns=["image ID", "cell ID", "num peroxisomes in cell", areacolname,
                                "total perox channel signal", "cytosolic perox signal",
                                "peroxisome ID", areacolname_PO, areacolnameinonly_PO,
                                "peroxisome signal", "peroxisome signal in cell"], index=False)
        set_column_widths(writer.sheets['ByPeroxisome'], df_PO, 30)  # set column widths

        df_OS.to_excel(writer, sheet_name='OtherStats',
                       columns=["Property", "Value"], index=False)
        set_column_widths(writer.sheets['OtherStats'], df_OS, 33)  # set column widths
        print("Finished segmenting cells and computating peroxisome metrics for " + tail)