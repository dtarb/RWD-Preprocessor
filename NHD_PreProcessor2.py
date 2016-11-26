import os
import sys
import fiona
from osgeo import ogr
import subprocess


from NHD_RWD_Utilities import complementary_gagewatershed, create_buffer, read_regionlist, read_gageids
#from DoMergeOGR import Do_Merge
#from DoMergeArcPro import Do_Merge


# calling %PY27% %ScriptDIR%NHD_PreProcessor2.py %InputDir% regionlist.txt


def main(input_dir_name, regionlistfile):

    (regions, subregions, regionfolders)=read_regionlist(input_dir_name, regionlistfile)
    RWDdir=os.path.join(input_dir_name,"RWDData")
    if not os.path.exists(RWDdir):
        os.mkdir(RWDdir)
    #regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    first=True
    mastergwfile = os.path.join(RWDdir, "gwmaster.shp")
    prjfile = os.path.join(RWDdir, "gwmaster.prj")  # It seems clunky to create this separately but could not figure out a better way
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(mastergwfile):
        shpdriver.DeleteDataSource(mastergwfile)
    masterds = shpdriver.CreateDataSource(mastergwfile)
    masterlyr = masterds.CreateLayer(mastergwfile, geom_type=ogr.wkbPolygon)

    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2

    id=0
    #regionfolder=[]
    downidlist=[]  # This is a list of lists giving [regionid, catch, catchdown] like [0, 139, 135], [0, 140, 139],
    dataind=[]   # This is just a list of catchment id's for indexing, like [139, 140].  It does not have to start at 0 (0r 1)
    for region in regionfolders:
        #regionfolder.append(region.strip())
        dataall1 = read_gageids(os.path.join(input_dir_name, "Regions",region, "id.txt"))
        for x in dataall1:
            downidlist.append([id]+x)    # This includes the element and region index in master list
            dataind=dataind+[x[0]]
        id=id+1  # this increments the region index

        gwfile = os.path.join(input_dir_name, "Regions",region, "gw.shp")
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
    print downidlist
    ncatch=len(downidlist)

    # Loop over downidlist.  If downid is -1, find corresponding catchmentid and look up if it falls in a polygon in master shapefile that is different from its id.  If it does, set this as downid
    masteridfile=os.path.join(RWDdir, "masterid.txt")
    mfile=open(masteridfile,'w')
    for i in xrange(0,ncatch):
        if(downidlist[i][downcatch] < 0):  # Here downid not known
            found=False
            regionid=downidlist[i][reg]
            region=regionfolders[regionid]
            catchOutfile = os.path.join(input_dir_name, "Regions",region, "catchOutlets3.shp")
            catchOutds = ogr.Open(catchOutfile)
            catchOutlyr = catchOutds.GetLayer()
            qstring="Id = " + str(downidlist[i][catch])
            catchOutlyr.SetAttributeFilter(qstring)
            for feature in catchOutlyr:
                # print feature.GetField("LINKNO")
                # Search over master polygond
                geom = feature.GetGeometryRef()
                masterlyr.SetSpatialFilter(geom)
                for mf in masterlyr:
                    idfound=mf.GetField("GRIDCODE")
                    if(downidlist[dataind.index(idfound)][reg] != regionid):  # if point is in different region
                        # It can occur that the outlet of catchment A in region 1 is in catchment B in region 2 and that catchment B in region 2 had already been connected to catchment A in region 1
                        # This occurs due to NHDPlus flow direcitons overlapping and being inconsistent along region edges.  This was found to occur in the Delaware estuary area at the edge of
                        # regions 02a and 02b.
                        # Making a connection here would result in a loop that fouls later recursion.  Check tracing down the path of the connection just found that
                        # Trace down function
                        def tracedown(idfound, thiscatch):
                            connectsback=False
                            nextdown=downidlist[dataind.index(idfound)][downcatch]
                            if(nextdown == thiscatch ):
                                connectsback=True
                                return(connectsback)
                            while(nextdown != -1):
                                nextdown = downidlist[dataind.index(nextdown)][downcatch]
                                if (nextdown == thiscatch):
                                    connectsback = True
                                    return (connectsback)
                            return(connectsback)

                        if(not tracedown(idfound,downidlist[i][catch])):
                            downidlist[i][downcatch]=idfound # set down pointer to where it is
                            print("Downstream connection made")
                            print("Catchment: "+ str(downidlist[i][catch])+ " to down: "+ str(idfound))
                        else:
                            print("No downstream connection made as it would create a loop")
                            print("Catchment: "+ str(downidlist[i][catch])+ " to down: "+ str(idfound))
                        if(found):
                            print("Possible error this point found previously")
                        found=True
            catchOutds.Destroy()  # close catchment data source
        # print master link file.
        mfile.write("%d %d %d\n" % (downidlist[i][reg],downidlist[i][catch],downidlist[i][downcatch]))
    masterds.Destroy()
    mfile.close()
    print("Done 2")


if __name__ == '__main__':
    main(*sys.argv[1:])



