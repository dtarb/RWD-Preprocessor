import shutil
import os
import subprocess
#from osgeo import ogr

import arcpy
from arcpy import env


def Do_Merge(input_dir_name, mergelist):
    subid = mergelist[0]
    destfolder=os.path.join(input_dir_name,"Subwatershed_ALL","Subwatershed%s" % subid)
    tempdir = os.path.join(destfolder,"temp")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir, ignore_errors=True)
    os.mkdir(tempdir)
    dissolvefile = os.path.join(destfolder, "Full_watershed%s.shp" % subid)
    # delete any file that may be there
    #driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(dissolvefile):
        #driver.DeleteDataSource(dissolvefile)
        arcpy.Delete_management(dissolvefile)

    f=open(os.path.join(destfolder,"upcatchids.txt"),"w")  # File to hold identifiers of upstream catchments to use in merging
    First = True
    ff=[]
    for id in mergelist:
        if (First):
            ff.append(os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % id, "subwatershed_%s.shp" % id))
            First = False
        else:  # For watersheds being merged in use the full watershed already developed
            ff.append(os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % id, "Full_watershed%s.shp" % id))
            f.write("%s\n" % str(id))
    f.close()
    if(len(ff)==1):  # just one file so use ogr2ogr copy
        ogr2ogr = "ogr2ogr " + dissolvefile + " " + ff[0]
        print(ogr2ogr)
        subprocess.check_call(ogr2ogr)
    else:  # Here call arcgis merge to avoid slivers
        os.chdir(destfolder)
        MergeDissolve(mergelist[0])
        #PROPY = r'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"'
        #MergeScript = r'"D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDPreproRepo\MergeArcPro.py"'
        #runmerge = PROPY + " " + MergeScript + " " + str(mergelist[0])
        #print(runmerge)
        #subprocess.check_call(runmerge)

    shutil.rmtree(tempdir, ignore_errors=True)

def read_Masterids(masterIDfile):
    downidlist = []
    upidlist = []
    catchdone = []
    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2
    with open(masterIDfile) as f:
        lines = f.read().splitlines()
    for x in lines:
        x1 = []
        for x2 in x.split():
            x1.append(int(x2))
        downidlist.append(x1)
    return (downidlist)


def MergeDissolve(catchid):
    """ Merge then dissolve features based on common attributes"""

    curwd = os.getcwd()
    env.workspace = curwd

    with open("upcatchids.txt", 'r') as f:
        lines = f.read().splitlines()
    upcatchids = [int(x) for x in lines]
    inputs="subwatershed_%s.shp"% catchid
    for upid in upcatchids:
        inputs=inputs+";"+os.path.join("..","Subwatershed%s" % upid,"Full_watershed%s.shp" % upid)
    tempoutput=os.path.join("temp","temp.shp")
    output="Full_watershed%s.shp"% catchid

    arcpy.management.Merge(inputs,tempoutput)
    arcpy.management.Dissolve(tempoutput,output)

def read_regionlist(input_dir_name, regionlistfile):
    with open(os.path.join(input_dir_name, regionlistfile), 'r') as f:
        lines = f.read().splitlines()
    regions = []
    subregions = []
    regionfolders = []
    for line in lines[1:]:
        ls = line.split()
        for sr in ls[1:]:
            subregions.append(sr)
            regionfolders.append("Reg" + sr)
            regions.append(ls[0])
    return (regions, subregions, regionfolders)

def mosaic_to_Raster(input_dir_name, regionlistfile):
    """mosaic all the gw rasters to a new raster"""
    # Existing rasters are in regNN/Main_Watershed/gw.tif
    # Results is in gwgrid.tif
    # All in input_dir_name
    (regions, subregions, regionfolders) = read_regionlist(input_dir_name, regionlistfile)

    #regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    #regionfolders = [region.strip() for region in regions]
    RWDDir="RWDData"
    os.chdir(input_dir_name)

    inrasters=""
    First=True

    for workname in regionfolders:
        if not First:
            inrasters=inrasters+";"
        inrasters=inrasters+os.path.join("Regions",workname,"gw.tif")
        First=False

    # delete if exists
    gwgridfile=os.path.join(RWDDir,"gwgrid.tif")
    if os.path.exists(gwgridfile):
        #driver.DeleteDataSource(dissolvefile)
        arcpy.Delete_management(gwgridfile)

# Note that use of .prj file below assumes gwmaster.shp file is already created following our naming in this folder
    prjfile=os.path.join(RWDDir,"gwmaster.prj")
    arcpy.management.MosaicToNewRaster(inrasters, RWDDir, "gwgrid.tif",prjfile,"32_BIT_UNSIGNED", None, 1, "LAST", "FIRST")
    print("Mosaic Done")