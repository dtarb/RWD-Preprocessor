import os
import sys

import arcpy
from arcpy import env


def main(input_dir_name, regionlistfile):
    """mosaic all the gw rasters to a new raster"""
    # Existing rasters are in regNN/Main_Watershed/gw.tif
    # Results is in gwgrid.tif
    # All in input_dir_name

    regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    regionfolders = [region.strip() for region in regions]
    os.chdir(input_dir_name)

    inrasters=""
    First=True

    for workname in regionfolders:
        if not First:
            inrasters=inrasters+";"
        inrasters=inrasters+os.path.join(workname,"Main_Watershed","gw.tif")
        First=False

# Note that use of .prj file below assumes gwmaster.shp file is already created following our naming in this folder
    arcpy.management.MosaicToNewRaster(inrasters, input_dir_name, "gwgrid.tif","gwmaster.prj","8_BIT_UNSIGNED", None, 1, "LAST", "FIRST")
    print("Mosaic Done")

if __name__ == '__main__':
    main(*sys.argv[1:])


