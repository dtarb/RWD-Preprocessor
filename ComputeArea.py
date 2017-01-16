import os
import glob
from osgeo import gdal, ogr

# This file holds work on adding attribute area to shapefiles involved in RWD.  Did not finish as found that on the fly calculation of area from shapefile was a small fraction of time compared to joining.
files = glob.glob("Subwatershed_ALL/*")
#print (files)
nfiles=len(files)
startdir = os.getcwd()
for subdir in files:
    print subdir
    os.chdir(startdir)
    os.chdir(subdir)

    files2=glob.glob("*Simple*.shp")
    print files2
    for file in files2:
        name=os.path.splitext(file)[0]
        sql="ALTER TABLE " + name + " DROP COLUMN Id"
        cmd='ogrinfo ' + file + ' -sql "' + sql + '"'
        print(cmd)
        os.system(cmd)
        sql = "ALTER TABLE " + name + " DROP COLUMN ORIG_FID"
        cmd = 'ogrinfo ' + file + ' -sql "' + sql + '"'
        print(cmd)
        os.system(cmd)

        source = ogr.Open(file, 1)
        layer = source.GetLayer()
        featureCount = layer.GetFeatureCount()
        new_field = ogr.FieldDefn('Area_km2', ogr.OFTReal)  # Changed field names to indicate units
        layer.CreateField(new_field)
        featureCount2 = layer.GetFeatureCount()
        feature = layer.GetFeature(0)
        fieldcount = feature.GetFieldCount()
        geom = feature.GetGeometryRef()
        area = geom.GetArea() / 1000000  # convert to km2
        feature.SetField(0,float(area))
        layer.SetFeature(feature)
        feature=None
        source = None



print("Done")
