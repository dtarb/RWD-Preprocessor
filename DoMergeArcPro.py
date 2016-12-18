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
    os.chdir(destfolder)
    MergeDissolve(mergelist[0])
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

    # From doing in ArcPro
    # arcpy.analysis.Buffer("subwatershed_1",
    #                       r"D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\NHDPlusTest\RWDData\Subwatershed_ALL\Subwatershed1\temp.shp",
    #                       "1 Meters", "FULL", "ROUND", "ALL", None, "PLANAR")

    insub="subwatershed_%s.shp"% catchid
    buffersub=r"temp\buff.shp"
    arcpy.analysis.Buffer(insub,buffersub,"1 Meters")  # Buffer each subwatershed before any merging and dissolving.  Full watersheds will then inherit the buffers
    with open("upcatchids.txt", 'r') as f:
        lines = f.read().splitlines()
    upcatchids = [int(x) for x in lines]
    inputs=os.path.join("temp","buff.shp")
    for upid in upcatchids:
        inputs=inputs+";"+os.path.join("..","Subwatershed%s" % upid,"Full_watershed%s.shp" % upid)
    tempoutput=os.path.join("temp","temp.shp")
    output="Full_watershed%s.shp"% catchid

    arcpy.management.Merge(inputs,tempoutput)
    arcpy.management.Dissolve(tempoutput,output)

def ElimPolyPart(catchid):
    """ Eliminate polygon parts"""

    curwd = os.getcwd()
    env.workspace = curwd

    # From doing in ArcPro
    # arcpy.management.EliminatePolygonPart("New_Point_Watershed", r"D:\RWD\NHDPlus\DelineatedWatershedCo\simpw.shp", "PERCENT", "0 SquareMeters", 99, "CONTAINED_ONLY")

    input = "Full_watershed%s.shp" % catchid
    output = "Simple_watershed%s.shp" % catchid
    arcpy.management.EliminatePolygonPart(input, output,"PERCENT", "0 SquareMeters", 99, "CONTAINED_ONLY")


def read_regionlist(input_dir_name, regionlistfile):
    # Regionlistfile format:
    # <header>
    # <region> <subregion1> <subregion2>
    # <region> <subregion3> < subregion4>
    # etc
    # Example
    # Regions and subregions to use
    # 08 08a 08b
    # 11 11c

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