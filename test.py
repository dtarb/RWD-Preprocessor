import os
import fiona
from fiona import collection
import shapefile
from shapely.ops import cascaded_union
from shapely.geometry import shape, mapping

input_dir_name="D:\\Dropbox\\Projects\\MMW2_StroudWPenn\\RWDWork\\NHDPlus\\cd1"
infile=os.path.join(input_dir_name,"gwmaster.shp")
dest=os.path.join(input_dir_name,"Subwatershed_ALL")

with fiona.open(infile) as source:
    meta = source.meta
    for f in source:
        outfile = os.path.join(dest, "Subwatershed%s" % int(f['properties']['GRIDCODE']))
        os.mkdir(outfile)
        outfile = os.path.join(outfile, "subwatershed_%s.shp" % int(f['properties']['GRIDCODE']))
        with fiona.open(outfile, 'w', **meta) as sink:
            sink.write(f)
            print(int(f['properties']['GRIDCODE']))

ids=[8,192,194,196]

mergfile1 = os.path.join(input_dir_name,"test1.shp")
mergfile2 = os.path.join(input_dir_name,"test2.shp")
#files.append(sub_water_file)
w = shapefile.Writer()
#for ff in files:
for id in ids:
    ff=os.path.join(input_dir_name,"Subwatershed_ALL","Subwatershed%s" % id,"subwatershed_%s.shp" % id)
    r = shapefile.Reader(ff)
    w._shapes.extend(r.shapes())
    w.records.extend(r.records())  # make DSI as integer value otherwise it will not work

w.fields = list(r.fields)
w.save(mergfile1)
#inputfile = 'Full_watershed' + str(int(f['properties']['GRIDCODE'])) + 'WD' + '.shp'
#outputfile = 'Full_watershed' + str(int(f['properties']['GRIDCODE'])) + '.shp'
infile_crs = source.crs
with collection(mergfile1, "r") as input_file_obj:
    schema = input_file_obj.schema.copy()
    with collection(mergfile2, "w", "ESRI Shapefile", schema, infile_crs) as output:
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
print("Done")
# with fiona.open(outfile, 'w', **meta) as sink:
#     sink.write(f)
#     input_dir = os.path.join(input_dir_name, "Main_Watershed")
#     infile = os.path.join(input_dir, watershed_file)
#     complimentary_subwatershed_file = os.path.join(input_dir_name, "Subwatershed", "Full_watershed")
#     output_dir1 = os.path.join(input_dir_name, "Subwatershed")
#     if not os.path.exists(input_dir):
#         os.makedirs(input_dir)
#     if not os.path.exists(output_dir1):
#         os.makedirs(output_dir1)
#     output_dir2 = os.path.join(input_dir_name, "Subwatershed_ALL")
#     if not os.path.exists(output_dir2):
#         os.makedirs(output_dir2)
#     os.chdir(input_dir)
#     buffer_distance = 900   # used 30 cells 30*30 for NHD data
#     watershed_id_file_dir = os.path.join(input_dir, watershed_id_file)
#     shutil.copy2(watershed_id_file_dir, output_dir1)
#     with fiona.open(infile) as source:
#         meta = source.meta
#         dest = output_dir1
#         for f in source:
#             outfile = os.path.join(dest, "subwatershed_%s.shp" % int(f['properties']['GRIDCODE']))
#             with fiona.open(outfile, 'w', **meta) as sink:
#                 sink.write(f)
#
#
# with open('D:\\Dropbox\\Projects\\MMW2_StroudWPenn\\RWDWork\\NHDPlus\\cd1\\reg8\\Main_Watershed\\id.txt') as f:
#     lines = f.read().splitlines()
# lines1=lines[1:]
# seven = 7
# numbers=[]
# for e in lines[1:]:
#     x1=[seven]
#     for x in e.split():
#         x1.append(int(x))
#     numbers.append(x1)
# #numbers =[[seven, int(x) for x in e.split()] for e in lines[1:]]
# print numbers

# for x in xrange(-1,3):
#     print(x)
#
# ds_in = drv.Open("MN.shp")  # Get the contents of the shape file
# lyr_in = ds_in.GetLayer(0)  # Get the shape file's first layer
#
# # Put the title of the field you are interested in here
# idx_reg = lyr_in.GetLayerDefn().GetFieldIndex("P_Loc_Nm")
#
# # If the latitude/longitude we're going to use is not in the projection
# # of the shapefile, then we will get erroneous results.
# # The following assumes that the latitude longitude is in WGS84
# # This is identified by the number "4326", as in "EPSG:4326"
# # We will create a transformation between this and the shapefile's
# # project, whatever it may be
# geo_ref = lyr_in.GetSpatialRef()
# point_ref = ogr.osr.SpatialReference()
# point_ref.ImportFromEPSG(4326)
# ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)
#
#
# def check(lon, lat):
#     # Transform incoming longitude/latitude to the shapefile's projection
#     [lon, lat, z] = ctran.TransformPoint(lon, lat)
#
#     # Create a point
#     pt = ogr.Geometry(ogr.wkbPoint)
#     pt.SetPoint_2D(0, lon, lat)
#
#     # Set up a spatial filter such that the only features we see when we
#     # loop through "lyr_in" are those which overlap the point defined above
#     lyr_in.SetSpatialFilter(pt)
#
#     # Loop through the overlapped features and display the field of interest
#     for feat_in in lyr_in:
#         print lon, lat, feat_in.GetFieldAsString(idx_reg)
#
#
# # Take command-line input and do all this
# check(float(sys.argv[1]), float(sys.argv[2]))
# # check(-95,47)