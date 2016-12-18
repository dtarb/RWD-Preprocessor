import shutil
import os
import sys

import arcpy
from arcpy import env


from DoMergeArcPro import Do_Merge, read_Masterids, mosaic_to_Raster, ElimPolyPart

def main(input_dir_name):
    # Now simplify all the full watersheds by eliminating internal parts

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

    # Now there are placeholder upidlist entries for each catchment that can be appended to in next pass
    for thiscatch in downidlist:
        subid=thiscatch[catch]
        subfolder = os.path.join(RWDdir, "Subwatershed_ALL", "Subwatershed%s" % subid)
        os.chdir(subfolder)
        ElimPolyPart(subid)
        print("Subwatershed %s Done" % subid)


    print("Simplify Done!")


if __name__ == '__main__':
    main(*sys.argv[1:])



