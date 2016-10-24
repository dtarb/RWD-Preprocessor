import os
import sys

import arcpy
from arcpy import env


def main(datadir, raster, shapefile):
    """ converts a raster dataset to polygon feature"""

    # Set environment settings
    env.workspace = datadir

    # Set local variables
    inRaster = raster
    outPolygons = os.path.join(datadir, shapefile)
    field = "VALUE"

    # Execute RasterToPolygon
    arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)

if __name__ == '__main__':
    datadir = sys.argv[1]
    raster = sys.argv[2]
    shapefile = sys.argv[3]

    main(datadir, raster, shapefile)


