import os
import sys
import fiona
from osgeo import ogr


from NHD_RWD_Utilities import complementary_gagewatershed, create_buffer


# calling %PY27% %ScriptDIR%NHD_PreProcessor2.py %InputDir% regionlist.txt


def main(input_dir_name, regionlistfile):
    regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    first=True
    mastergwfile = os.path.join(input_dir_name, "gwmaster.shp")
    prjfile = os.path.join(input_dir_name, "gwmaster.prj")  # It seems clunky to create this separately but could not figure out a better way
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(mastergwfile):
        shpdriver.DeleteDataSource(mastergwfile)
    masterds = shpdriver.CreateDataSource(mastergwfile)
    masterlyr = masterds.CreateLayer(mastergwfile, geom_type=ogr.wkbPolygon)

    id=0
    regionfolder=[]
    dataall = []
    for region in regions:
        regionfolder.append(region.strip())
        gageIDfile = os.path.join(input_dir_name, regionfolder[id], "Main_Watershed", "id.txt")
        with open(gageIDfile) as f:
            lines = f.read().splitlines()
        for e in lines[1:]:
            x1 = [id]  # id as a list
            for x in e.split():
                x1.append(int(x))
            dataall.append(x1)
        id=id+1

        gwfile = os.path.join(input_dir_name, region.strip(), "Main_Watershed", "gw.shp")
        inputds = ogr.Open(gwfile)
        inputlyr = inputds.GetLayer()
        if first:
            first=False
            # replicate fields in output
            inLayerDefn = inputlyr.GetLayerDefn()
            for i in range(0, inLayerDefn.GetFieldCount()):
                fieldDefn = inLayerDefn.GetFieldDefn(i)
                masterlyr.CreateField(fieldDefn)
            featureDefn = masterlyr.GetLayerDefn()
            spatialRef = inputlyr.GetSpatialRef()
            spatialRef.MorphToESRI()
            file = open(prjfile, 'w')
            file.write(spatialRef.ExportToWkt())
            file.close()

        nfeature=inputlyr.GetFeatureCount()
        for inFeature in inputlyr:
            # Create output Feature
            outFeature = ogr.Feature(featureDefn)
            # Add field values from input Layer
            for i in range(0, featureDefn.GetFieldCount()):
                outFeature.SetField(featureDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
                # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            masterlyr.CreateFeature(outFeature)
            #print inFeature.GetField("GRIDCODE")
            #print geom.Centroid().ExportToWkt()
            masterlyr.SyncToDisk()
        inputds.Destroy()  # Close region gage watershed file
    print dataall
    ncatch=len(dataall)

    # Loop over dataall.  If downid is -1, find corresponding catchmentid and look up if it falls in a polygon in master shapefile that is different from its id.  If it does, set this as downid
    masteridfile=os.path.join(input_dir_name, "masterid.txt")
    mfile=open(masteridfile,'w')
    for i in xrange(0,ncatch):
        if(dataall[i][2] < 0):  # Here downid not known
            found=False
            regionid=dataall[i][0]
            region=regionfolder[regionid]
            catchOutfile = os.path.join(input_dir_name, region, "Main_Watershed", "catchOutlets3.shp")
            catchOutds = ogr.Open(catchOutfile)
            catchOutlyr = catchOutds.GetLayer()
            qstring="Id = " + str(dataall[i][1])
            catchOutlyr.SetAttributeFilter(qstring)
            for feature in catchOutlyr:
                # print feature.GetField("LINKNO")
                # Search over master polygond
                geom = feature.GetGeometryRef()
                masterlyr.SetSpatialFilter(geom)
                for mf in masterlyr:
                    idfound=mf.GetField("GRIDCODE")
                    if(dataall[idfound-1][0] != regionid):  # if point is in different region
                        dataall[i][2]=idfound # set down pointer to where it is
                        print("Downstream connection made")
                        print("Catchment: "+ str(dataall[i][1])+ " to down: "+ str(idfound))
                        if(found):
                            print("Possible error this point found previously")
                        found=True
            catchOutds.Destroy()  # close catchment data source
        # print master link file.
        mfile.write("%d %d %d\n" % (dataall[i][0],dataall[i][1],dataall[i][2]))
    masterds.Destroy()
    mfile.close()

#  Write single shapefiles
    infile=os.path.join(input_dir_name,"gwmaster.shp")
    dest=os.path.join(input_dir_name,"Subwatershed_ALL")
    os.mkdir(dest)
    with fiona.open(infile) as source:
        meta = source.meta
        for f in source:
            outfile = os.path.join(dest, "Subwatershed%s" % int(f['properties']['GRIDCODE']))
            os.mkdir(outfile)
            outfile = os.path.join(outfile, "subwatershed_%s.shp" % int(f['properties']['GRIDCODE']))
            with fiona.open(outfile, 'w', **meta) as sink:
                sink.write(f)
                #print(int(f['properties']['GRIDCODE']))
    print("Done")

if __name__ == '__main__':
    main(*sys.argv[1:])



