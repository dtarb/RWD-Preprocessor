import shutil
import os
import fiona
from fiona import collection
import shapefile
from shapely.ops import cascaded_union
from shapely.geometry import shape, mapping

def Do_Merge(input_dir_name, mergelist):
    subid = mergelist[0]
    infile=os.path.join(input_dir_name,"gwmaster.shp")
    dest=os.path.join(input_dir_name,"Subwatershed_ALL","Subwatershed%s" % subid)

    with fiona.open(infile) as source:
        #meta = source.meta
        tempfolder = os.path.join(dest,"temp")
        mergefile = os.path.join(tempfolder,"temp.shp")
        os.mkdir(tempfolder)
        dissolvefile = os.path.join(dest,"Full_watershed%s.shp" % subid)
        w = shapefile.Writer()
        First=True
        for id in mergelist:
            if(First):
                ff=os.path.join(input_dir_name,"Subwatershed_ALL","Subwatershed%s" % id,"subwatershed_%s.shp" % id)
                First=False
            else:   # For watersheds being merged in use the full watershed already developed
                ff = os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % id, "Full_watershed%s.shp" % id)
            r = shapefile.Reader(ff)
            w._shapes.extend(r.shapes())
            w.records.extend(r.records())  # make DSI as integer value otherwise it will not work

        w.fields = list(r.fields)
        w.save(mergefile)
        #inputfile = 'Full_watershed' + str(int(f['properties']['GRIDCODE'])) + 'WD' + '.shp'
        #outputfile = 'Full_watershed' + str(int(f['properties']['GRIDCODE'])) + '.shp'
        infile_crs = source.crs
        with collection(mergefile, "r") as input_file_obj:
            schema = input_file_obj.schema.copy()
            with collection(dissolvefile, "w", "ESRI Shapefile", schema, infile_crs) as output:
                shapes = []
                for f in input_file_obj:
                    shapes.append(shape(f['geometry']).buffer(1))
                merged = cascaded_union(shapes)
                output.write({
                    'properties': {
                        'GRIDCODE': '1'
                    },
                    'geometry': mapping(merged)
                })
        shutil.rmtree(tempfolder, ignore_errors=True)
