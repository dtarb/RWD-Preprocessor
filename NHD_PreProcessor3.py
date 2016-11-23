import shutil
import os
import sys

import arcpy
from arcpy import env


from DoMergeArcPro import Do_Merge, read_Masterids, mosaic_to_Raster

def main(input_dir_name, regionlistfile):
    # Now do the recursion to join shapes
    # make upidlist by pass through appending downid
    # then pass over catchments
    # If no catchments upstream watershed file is subwatershed file.  Flag as done
    # If there are catchments upstream
    #    go there recursively
    #    write subwatershed file
    #    write watershed file as merge of upstream watershed files

    #  Data structures are
    # downidlist. A list of lists giving [regionid, catch, catchdown] like [[0, 139, 135], [0, 140, 139]]
    # dataind.  A list of catchment id's for indexing, like [139, 140].  It does not have to start at 0 (0r 1)
    # dataind and downidlist are the same length and logically paired element to element
    # upidlist.  A list of indexes to upstream catchments.  Like [[0, 2],[],[3,4]].  Note that these are indexes into the position in downidlist and dataind, not the values themselves ids

    RWDdir=os.path.join(input_dir_name,"RWDData")

    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2

    downidlist = read_Masterids(os.path.join(RWDdir,"masterid.txt"))
    upidlist = []
    catchdone = []
    dataind = []  # This is just a list of catchment id's for indexing, like [139, 140].  It does not have to start at 0 (0r 1)
    id = 0

    for i in range(len(downidlist)):
        # for thiscatch in downidlist:
        thiscatch=downidlist[i]
        dataind=dataind+[thiscatch[catch]]
        x1 = []
        upidlist.append(x1)  # append empty list placeholders for upid's
        catchdone.append(False)
    # Now there are placeholder upidlist entries for each catchment that can be appended to in next pass
    for thiscatch in downidlist:
        if (thiscatch[downcatch] > 0):  # this catchment has a downid so record this catchment as this downid's upid
            upentry = dataind.index(thiscatch[downcatch])  # the index to downcatch in the overall lists
            upidlist[upentry].append(dataind.index(thiscatch[catch]))  # append the index to this catchment
    print(upidlist)

    # Define the recursive function
    def catchmerge(idtomerge):
        if not catchdone[idtomerge]:
            listtomerge = [dataind[idtomerge]]
            num = len(upidlist[idtomerge])
            if (num > 0):
                for idup in upidlist[idtomerge]:
                    catchmerge(idup)
                    listtomerge.append(dataind[idup])
            catchdone[idtomerge] = True
            print(listtomerge)
            Do_Merge(RWDdir, listtomerge)

    # Now we do the recursive pass
    for indcatch in range(len(downidlist)):
        num = len(upidlist[indcatch])
        if (num > 0):
            for idup in upidlist[indcatch]:
                catchmerge(idup)
        catchmerge(indcatch)
        print("done " + str(downidlist[indcatch][catch]))

    # Last step Mosaic to raster
    mosaic_to_Raster(input_dir_name, regionlistfile)
    #PROPY = r'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"'
    #MosaicScript = r'"D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDPreproRepo\mosaicToRaster.py"'
    #runmosaic = PROPY + " " + MosaicScript + " " + input_dir_name + " " + regionlistfile
    #print(runmosaic)
    #subprocess.check_call(runmosaic)

    print("Finally Done!")


if __name__ == '__main__':
    main(*sys.argv[1:])



