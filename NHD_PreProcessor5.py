import os
import sys
import subprocess
import shutil

import arcpy
from arcpy import env

from DoMergeArcPro import read_regionlist

def mosaic_Regions(input_dir_name, regionlistfile):
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

# This preprocessor code to set up the handling of grid cells outside of partitioned gage watersheds
def main(input_dir_name, regionlistfile, FirstRegionid):

    (regions, subregions, regionfolders) = read_regionlist(input_dir_name, regionlistfile)

    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2

    region_area_ids = {'01': 'NE', '02': 'MA', '03N': 'SA', '03S': 'SA', '03W': 'SA', '04': 'GL', '05': 'MS',
                       '06': 'MS', '07': 'MS', '08': 'MS', '09': 'SR', '10L': 'MS', '10U': 'MS', '11': 'MS',
                       '12': 'TX', '13': 'RG', '14': 'CO', '15': 'CO', '16': 'GB', '17': 'PN', '18': 'CA',
                       '20': 'HI', '21': 'CI', '22AS': 'PI', '22GU': 'PI', '22MP': 'PI'}
    #maxId = int(FirstCatchid)-1
    temp = os.path.join(input_dir_name, "RWDData")
    RWDdir = os.path.join(temp, "Main_Watershed")
    SWDdir = os.path.join(temp, "Subwatershed_ALL")
    if not os.path.exists(RWDdir):
        return False   # bail if RWDDir does not exist
    if not os.path.exists(SWDdir):
        return False  # bail if SWDDir does not exist

    Regdir=os.path.join(input_dir_name,"Regions")
    if not os.path.exists(Regdir):
        return False  # bail if RWDDir does not exist

    mosaiclist=[]

    for ireg in range(len(regionfolders)):
        regid = int(FirstRegionid)+ireg
        workname = regionfolders[ireg]
        region=regions[ireg]
        subregion=subregions[ireg]
        workfolder = os.path.join(input_dir_name,"Regions",workname)
        mosaiclist.append(os.path.join(workfolder,"region.tif"))
        if os.path.exists(workfolder):  # Here the region folder exists so run the setregions function
            os.chdir(workfolder)
            cmd = "mpiexec -n 8 setregion -p fdr.tif -gw gw.tif -out region.tif -id " + str(regid)
            subprocess.check_call(cmd)
            Regiondir=os.path.join(SWDdir,"Region%s" % str(regid))
            if not os.path.exists(Regiondir):
                os.mkdir(Regiondir)
            destination=os.path.join(Regiondir,"Region_%sp.tif" % str(regid))
            shutil.copy("fdr.tif",destination)



    # Here we have done created local region files for each region
    prjfile = os.path.join(RWDdir, "gwmaster.prj")
    arcpy.management.MosaicToNewRaster(mosaiclist, RWDdir, "regions.tif", prjfile, "32_BIT_UNSIGNED", None, 1,
                                               "LAST", "FIRST")


if __name__ == '__main__':
    main(*sys.argv[1:])



