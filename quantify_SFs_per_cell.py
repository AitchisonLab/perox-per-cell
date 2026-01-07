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
# maskdir: output directory for subcellular feature and cell masks
# SFdotcut: Subcellular feature segmentation sensitivity parameter
# SFminarea: Minimum area for subcellular feature
# cellminarea: Minimum area for cells
# maxintensity: Theoretical maximum intensity level of input images
# version: Software version
def quantify_and_save(sourceimagepath, maskdir, SFdotcut, SFminarea, cellminarea, maxintensity, cellsegmenter, version):

    head, tail = os.path.split(sourceimagepath)
    fileid = tail

    # Get masks and count number of subcellular features per cell
    print("Counting subcellular features per cell for " + fileid)
    cells = maskdir + os.path.splitext(fileid)[0] + '.tif'  # Segmented cells mask
    subfeat = maskdir + fileid + '_subcellularfeatures_labeled_objects.tiff'  # Segmented subcellular features mask
    rawzprojsubfeat = sourceimagepath + '_Zprojections/subcellularfeatures/' + fileid + '_subcellularfeatures_Zprojection.tiff'

    cellseg = imread(cells)
    subfeatseg = imread(subfeat)
    subfeatrawz = imread(rawzprojsubfeat)

    # Collect pixel physical area stored in labeled subcellular feature image
    frames = TiffFile(subfeat)
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
    cytoSFsignal = []
    totalSFsignal = []
    totalSFarea = []
    SFsAssignedToOtherCellsSignal = []

    # Set up similar arrays for the excel sheet that lists all subcellular features
    image_id_SF = []
    cell_id_SF = []
    num_per_SF = []
    cell_area_SF = []
    cytoSFsignal_SF = []
    totalSFsignal_SF = []
    subfeat_id_SF = []
    subfeat_area_SF = []
    subfeat_area_in_cell_SF = []
    subfeat_signal_SF = []
    subfeat_signal_in_cell_SF = []

    maxcellid = 0
    print("Num cell ids: " + str(len(np.unique(cellseg[cellseg > 0]))))
    if len(np.unique(cellseg[cellseg > 0])) > 0:
        cellids = [i for i in np.unique(cellseg) if i > 0]
        maxcellid = np.max(cellids)
    else:
        cellids = []

    maxsubfeatid = 0
    print("Num subcellular feature ids: " + str(len(np.unique(subfeatseg[subfeatseg > 0]))))
    if len(np.unique(subfeatseg[subfeatseg > 0])) > 0:
        subfeatids = [j for j in np.unique(subfeatseg) if j > 0]
        maxsubfeatid = np.max(subfeatids)
    else:
        subfeatids = []

    subfeatidsnotincells = subfeatids.copy()

    # Populate arrays that record the overlap between cells and subcellular features
    # as well as the signal intensity in those overlapping regions
    # This ensures that each subcellular feature is assigned to only one cell

    SFcellArrayOverlap = np.zeros((int(maxsubfeatid) + 1, int(maxcellid) + 1), dtype=np.float)  # Initialize
    SFcellArrayIntensity = np.zeros((int(maxsubfeatid) + 1, int(maxcellid) + 1), dtype=np.float)  # Initialize

    print("Assigning subcellular features to cells")
    for i in cellids:
        cellmask = cellseg.copy()
        cellmask[cellseg != i] = 0
        cellmask[cellmask > 0] = 1

        # Get subcellular features inside cell boundary (even if cell is on edge), exclude 0 values
        subfeatsegmaskincell = subfeatseg * cellmask  # only includes segmented subcellular features within cell
        subfeatidsincell = [k for k in np.unique(subfeatsegmaskincell) if k > 0]

        # Record number of overlapping pixels and summed intensity within cell for each subcellular feature that overlaps with cell
        for p in subfeatidsincell:
            subfeatsegmaskincellcopy = subfeatsegmaskincell.copy()
            subfeatsegmaskincellcopy[subfeatsegmaskincellcopy != p] = 0
            subfeatsegmaskincellcopy[subfeatsegmaskincellcopy > 0] = 1
            SFoverlapVal = np.sum(subfeatsegmaskincellcopy)

            subfeatrawoneSF = subfeatsegmaskincellcopy * subfeatrawz
            SFintensityVal = np.sum(subfeatrawoneSF)

            # Check if this same subcellular feature has already been assigned a cell
            SFoverlaps = SFcellArrayOverlap[int(p)]
            alreadyassigned = len(SFoverlaps[SFoverlaps != 0]) > 0

            if alreadyassigned:
                assignSFtocell = False
                # Compare num. overlapping pixels
                maxexistingoverlap = max(
                    SFcellArrayOverlap[int(p)])  # Maximum value in row representing overlaps with cells
                existingcellindex = np.argmax(SFcellArrayOverlap[int(p)])  # Index of maximum value

                if maxexistingoverlap > SFoverlapVal:
                    continue  # Skip this subcellular feature because it should be assigned to a different cell
                elif maxexistingoverlap < SFoverlapVal:
                    assignSFtocell = True
                else:  # If the subcellular feature's area is equally shared among cells...
                    # Compare the summed intensity values
                    maxexistingintensity = max(SFcellArrayIntensity[int(p)])

                    if maxexistingintensity > SFintensityVal:
                        continue  # Skip this subcellular feature because it should be assigned to a different cell
                    elif maxexistingintensity < SFintensityVal:
                        assignSFtocell = True
                    else:  # If the subcellular feature's area is perfectly split between multiple cells as well as its signal...
                        # Coin flip to decide whether to assign feature to cell or keep the existing assignment
                        assignSFtocell = random.choice([True, False])

                if assignSFtocell:
                    # Replace the existing overlap and intensity values with zeros
                    SFcellArrayOverlap[int(p)][existingcellindex] = 0
                    SFcellArrayIntensity[int(p)][existingcellindex] = 0

            # If we're here it means we should assign the subcellular feature to the cell
            SFcellArrayOverlap[int(p)][int(i)] = SFoverlapVal  # Record n pixels overlapping
            SFcellArrayIntensity[int(p)][int(i)] = SFintensityVal  # Record summed intensity of overlapping pixels

    # For each cell, collect metrics
    for i in cellids:
        # Get num subcellular features and other metrics for the current cell
        cellmask = cellseg.copy()
        cellmask[cellseg != i] = 0
        cellmask[cellmask > 0] = 1

        # Get subcellular features assigned to cell boundary (even if cell is on edge), exclude 0 values
        subfeatidsincell = np.argwhere(SFcellArrayOverlap[:, int(i)] != 0)
        subfeatidsnotincells = np.setdiff1d(subfeatidsnotincells, subfeatidsincell)

        if i in edgecells:  # skip if it's a cell on the image border
            continue

        if (i % 10) == 0:  # report progress
            print("Finished ", str(int(i)), " of ", str(int(np.max(cellids))), " cells")

        npixels = np.sum(cellmask)
        carea = float(pixarea) * float(npixels)  # cell area
        per = subfeatseg * cellmask  # only includes segmented features within cell (can include features assigned to other cells)
        per_num = len(subfeatidsincell)  # get number of unique subcellular features in cell. minus one to remove 0 value
        image_id.append(fileid)
        cell_id.append(i)
        num_per.append(per_num)
        cell_area.append(carea)

        # Get cytosolic subcellular feature signal within the cell using the maximum Z-projection of the
        # original subcellular feature image
        singlecellrawsubfeat = subfeatrawz * cellmask  # exclude all signal not within cell boundary
        singlecellrawsubfeattot = singlecellrawsubfeat.copy()
        totalSFsignalval = np.sum(singlecellrawsubfeattot)
        totalSFsignal.append(totalSFsignalval)
        singlecellrawsubfeat[per != 0] = 0  # Remove segmented subcellular features from raw signal
        cytoSFsignalval = np.sum(singlecellrawsubfeat)
        cytoSFsignal.append(cytoSFsignalval)

        # Add in total subcellular feature area in cell
        perbinary = per.copy()
        perbinary[perbinary > 0] = 1
        nsubfeatpixels = np.sum(perbinary)
        totalSFareaval = float(pixarea) * float(nsubfeatpixels)
        totalSFarea.append(totalSFareaval)

        # Collect the signal from features that overlap with this cell but were assigned to other cells
        # because they overlapped more with other cells or were split evenly but had a higher signal
        # in other cells (or were randomly assigned to other cells).
        # First get signal from all segmented features within cell bounds
        subfeatsegassignedothers = per

        for k in subfeatidsincell:  # k values are ints
            # signal from segmented features within cell bounds that were assigned to other cells
            subfeatsegassignedothers[subfeatsegassignedothers == k] = 0

        subfeatsegassignedothers[subfeatsegassignedothers > 0] = 1  # Make binary
        singlecellrawsubfeatotherassign = singlecellrawsubfeattot * subfeatsegassignedothers
        SFsAssignedToOtherCellsSignal.append(np.sum(singlecellrawsubfeatotherassign))

        # For each subcellular feature assigned to the cell, collect metrics
        for p in subfeatidsincell:
            image_id_SF.append(fileid)
            cell_id_SF.append(i)
            num_per_SF.append(per_num)
            cell_area_SF.append(carea)
            cytoSFsignal_SF.append(cytoSFsignalval)
            totalSFsignal_SF.append(totalSFsignalval)
            subfeat_id_SF.append(int(p))

            subfeatsegmask = subfeatseg.copy()  # Includes all of the subcellular feature, even if outside of cell bounds
            subfeatsegmask[subfeatsegmask != p] = 0
            subfeatsegmask[subfeatsegmask > 0] = 1
            npixels_SF = np.sum(subfeatsegmask)
            parea = float(pixarea) * float(npixels_SF)  # complete subcellular feature area, including pixels outside of cell
            subfeat_area_SF.append(parea)

            npixels_in_cell_SF = SFcellArrayOverlap[int(p)][int(i)]
            sfareaincell = float(pixarea) * float(npixels_in_cell_SF)  # subcellular feature area that is inside the cell
            subfeat_area_in_cell_SF.append(sfareaincell)

            # Add in total intensity for individual feature (this includes the full segmented feature, not just the part in the cell)
            singlesubfeatraw = subfeatrawz * subfeatsegmask  # exclude all signal not within subcellular feature
            singlesubfeatsignal = np.sum(singlesubfeatraw)
            subfeat_signal_SF.append(singlesubfeatsignal)

            # Collect the intensity of the part of the feature that was in the cell (usually the same as the full feature)
            singlesubfeatsignalincell = SFcellArrayIntensity[int(p)][int(i)]
            subfeat_signal_in_cell_SF.append(singlesubfeatsignalincell)

    # Format data frame for "ByCell" sheet
    df = pd.DataFrame({'image ID': image_id, 'cell ID': cell_id, 'num subcellular features in cell': num_per,
                       'cell area': cell_area, 'total subcellular feature area in cell': totalSFarea,
                       'total subcellular feature channel signal': totalSFsignal,
                       'cytosolic subcellular feature signal': cytoSFsignal,
                       'signal from subcellular features assigned to other cells': SFsAssignedToOtherCellsSignal})
    areacolname = 'cell area (' + pixareaunits + ')'
    subfeatareacolname = 'total subcellular feature area in cell (' + pixareaunits + ')'
    df.rename(columns={'cell area': areacolname}, inplace=True)
    df.rename(columns={'total subcellular feature area in cell': subfeatareacolname}, inplace=True)

    # Format data frame for "BySubcellularFeature" sheet
    df_SF = pd.DataFrame({'image ID': image_id_SF,
                          'cell ID': cell_id_SF,
                          'num subcellular features in cell': num_per_SF,
                          'cell area': cell_area_SF,
                          'total feature channel signal': totalSFsignal_SF,
                          'cytosolic feature signal': cytoSFsignal_SF,
                          'feature ID': subfeat_id_SF,
                          'feature area': subfeat_area_SF,
                          'feature area in cell': subfeat_area_in_cell_SF,
                          'feature signal': subfeat_signal_SF,
                          'feature signal in cell': subfeat_signal_in_cell_SF})
    df_SF.rename(columns={'cell area': areacolname}, inplace=True)
    areacolname_SF = 'feature area (' + pixareaunits + ')'
    df_SF.rename(columns={'feature area': areacolname_SF}, inplace=True)
    areacolnameinonly_SF = 'feature area in cell (' + pixareaunits + ')'
    df_SF.rename(columns={'feature area in cell': areacolnameinonly_SF}, inplace=True)

    # Other stats
    properties = []
    values = []

    subfeatoutsideval = len(subfeatidsnotincells)
    properties.append("N subcellular features outside cells")
    values.append(subfeatoutsideval)

    subfeatoutsidefracval = "N/A"

    if len(subfeatids) > 0:
        subfeatoutsidefracval = float(subfeatoutsideval) / float(len(subfeatids))

    properties.append("Fraction of subcellular features outside cells")
    values.append(subfeatoutsidefracval)

    properties.append("File processed")
    values.append(sourceimagepath.replace('\\', '/'))  # Sometimes there is a mix of / and \ in file path (?)

    properties.append("SFdotcut")
    values.append(SFdotcut)

    properties.append("SFminarea")
    values.append(SFminarea)

    properties.append("cellminarea")
    values.append(cellminarea)

    properties.append("maxintensity")
    values.append(maxintensity)

    properties.append("CellSegmenter")
    values.append(cellsegmenter)

    properties.append("feature-per-cell version")
    values.append(version)

    df_OS = pd.DataFrame({'Property': properties, 'Value': values})

    with pd.ExcelWriter(head + '/' + fileid + '_feature_per_cell.xlsx') as writer:

        df.to_excel(writer, sheet_name='ByCell',
                    columns=["image ID", "cell ID", "num subcellular features in cell", areacolname, subfeatareacolname,
                             "total subcellular feature channel signal", "cytosolic subcellular feature signal",
                             "signal from subcellular features assigned to other cells"], index=False)
        set_column_widths(writer.sheets['ByCell'], df, 40)  # set column widths

        df_SF.to_excel(writer, sheet_name='BySubcellularFeature',
                       columns=["image ID", "cell ID", "num subcellular features in cell", areacolname,
                                "total feature channel signal", "cytosolic feature signal",
                                "feature ID", areacolname_SF, areacolnameinonly_SF,
                                "feature signal", "feature signal in cell"], index=False)
        set_column_widths(writer.sheets['BySubcellularFeature'], df_SF, 30)  # set column widths

        df_OS.to_excel(writer, sheet_name='OtherStats',
                       columns=["Property", "Value"], index=False)
        set_column_widths(writer.sheets['OtherStats'], df_OS, 40)  # set column widths
        print("Finished segmenting cells and computing subcellular feature metrics for " + tail)