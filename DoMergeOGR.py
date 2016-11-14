import shutil
import os
import subprocess


def Do_Merge(input_dir_name, mergelist):
    subid = mergelist[0]
    destfolder=os.path.join(input_dir_name,"Subwatershed_ALL","Subwatershed%s" % subid)
    tempdir = os.path.join(destfolder,"temp")
    os.mkdir(tempdir)
    dissolvefile = os.path.join(destfolder, "Full_watershed%s.shp" % subid)
    tempfile = os.path.join(tempdir,"temp.shp")
    #  Commands needed
    # ogr2ogr temp1.shp first.shp
    # for 2nd to nth
    # ogr2ogr -update -append temp1.shp next.shp
    # ogr2ogr dissolve.shp temp.shp -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM Full_watershed4ogr"

    f=open(os.path.join(destfolder,"upcatchids.txt"),"w")  # File to hold identifiers of upstream catchments to use in merging
    First = True
    for id in mergelist:
        if (First):
            ff = os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % id, "subwatershed_%s.shp" % id)
            ogr2ogr = "ogr2ogr " + tempfile + " " + ff
            print(ogr2ogr)
            subprocess.check_call(ogr2ogr)
            First = False
        else:  # For watersheds being merged in use the full watershed already developed
            ff = os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % id, "Full_watershed%s.shp" % id)
            ogr2ogr = "ogr2ogr -update -append " + tempfile + " " + ff
            print(ogr2ogr)
            subprocess.check_call(ogr2ogr)
            f.write("%s\n" % str(id))
    f.close()
    ogr2ogr= "ogr2ogr " + dissolvefile + " " + tempfile + " -dialect sqlite -sql "
    sqltext="SELECT ST_Union(geometry) AS geometry FROM " + "temp"
    ogr2ogr = ogr2ogr + '"'+sqltext +'"'
    print(ogr2ogr)
    subprocess.check_call(ogr2ogr)
    shutil.rmtree(tempdir, ignore_errors=True)

