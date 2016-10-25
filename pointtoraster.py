import os
import sys

import arcpy
from arcpy import env


def main(datadir, pointfile, refraster, outfile):
    """ coverts feature to raster"""

    # Set environment settings
    env.workspace = datadir

    # Local variables:
    dp_file = os.path.join(env.workspace,  pointfile)
    wt_tif = os.path.join(env.workspace, outfile)
    arcpy.env.extent = os.path.join(env.workspace, refraster)
    arcpy.env.outputCoordinateSystem = os.path.join(env.workspace, refraster)
    cellsize = 30

    # Process: Feature to Raster
    arcpy.FeatureToRaster_conversion(dp_file, "Gval", wt_tif, cellsize)

if __name__ == '__main__':
    datadir = sys.argv[1]
    pointfile = sys.argv[2]
    refraster = sys.argv[3]
    outfile = sys.argv[4]
    main(datadir, pointfile, refraster, outfile)


