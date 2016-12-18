import os
import glob
import zipfile
import sys
from DoMergeArcPro import Do_Merge, read_Masterids

def main(input_dir_name):
    # Now simplify all the full watersheds by eliminating internal parts

    RWDdir=os.path.join(input_dir_name,"RWDData")
    os.chdir(RWDdir)
    zf = zipfile.ZipFile("Simple.zip", "w", allowZip64=True)

    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2

    downidlist = read_Masterids(os.path.join(RWDdir,"masterid.txt"))
    upidlist = []
    catchdone = []
    dataind = []  # This is just a list of catchment id's for indexing, like [139, 140].  It does not have to start at 0 (0r 1)
    id = 0

    # Now there are placeholder upidlist entries for each catchment that can be appended to in next pass
    for thiscatch in downidlist:
        subid=thiscatch[catch]
        subdir = os.path.join("Subwatershed_ALL", "Subwatershed%s" % subid)
        files = glob.glob(subdir+"/Simple*")
        for file in files:
            zf.write(file)
        print("Subwatershed %s Done" % subid)
    zf.close()

    print("Simple zip done!")





if __name__ == '__main__':
    main(*sys.argv[1:])




