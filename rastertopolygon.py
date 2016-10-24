# Name: RasterToPolygon_Ex_02.py
# Description: Converts a raster dataset to polygon features.
# Requirements: None

# Import system modules
import sys
import arcpy
from arcpy import env

def rastertoPolygon(datadir, raster, shapefile):
    # Set environment settings
    env.workspace = datadir

    # Set local variables
    inRaster = raster
    outPolygons =datadir+"/"+shapefile
    field = "VALUE"

    # Execute RasterToPolygon
    arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)
if __name__ == '__main__':
    datadir = sys.argv[1]
    raster = sys.argv[2]
    shapefile=sys.argv[3]

    rastertoPolygon(datadir, raster, shapefile)


