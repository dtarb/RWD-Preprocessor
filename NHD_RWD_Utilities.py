import os
import os.path

import pandas as pd
import numpy as np

from osgeo import ogr


def create_buffer(input_file_name, output_buffer_file, buffer_distance):
    inputds = ogr.Open(input_file_name)
    inputlyr = inputds.GetLayer()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(output_buffer_file):
        shpdriver.DeleteDataSource(output_buffer_file)
    outputBufferds = shpdriver.CreateDataSource(output_buffer_file)
    bufferlyr = outputBufferds.CreateLayer(output_buffer_file, geom_type=ogr.wkbPolygon)
    featureDefn = bufferlyr.GetLayerDefn()

    for feature in inputlyr:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(buffer_distance)
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geomBuffer)
        bufferlyr.CreateFeature(outFeature)

def read_regionlist(input_dir_name, regionlistfile):
    with open(os.path.join(input_dir_name, regionlistfile), 'r') as f:
        lines=f.read().splitlines()
    regions = []
    subregions = []
    regionfolders = []
    for line in lines[1:]:
        ls = line.split()
        for sr in ls[1:]:
            subregions.append(sr)
            regionfolders.append("Reg" + sr)
            regions.append(ls[0])
    return(regions,subregions,regionfolders)

def read_gageids(gageIDfile):
    dataall = []
    with open(gageIDfile) as f:
        lines = f.read().splitlines()
    for e in lines[1:]:
        x1 = []  # id as a list
        for x in e.split():
            x1.append(int(x))
        dataall.append(x1)
    return(dataall)

    with open(os.path.join(input_dir_name, regionlistfile), 'r') as f:
        lines=f.read().splitlines()
    regions = []
    subregions = []
    regionfolders = []
    for line in lines[1:]:
        ls = line.split()
        for sr in ls[1:]:
            subregions.append(sr)
            regionfolders.append("Reg" + sr)
            regions.append(ls[0])
    return(regions,subregions,regionfolders)

def complementary_gagewatershed(gageIDfile, num):
    data = np.loadtxt(gageIDfile, skiprows=1)
    df = pd.DataFrame(data=data, columns=['id', 'iddown'])

    up1 = []
    up2 = []

    def upstream_watershed(num):
        if num == -1:
            up2.append(-1)
            return up2
        else:
            mask = df[['iddown']].isin([num]).all(axis=1)
            data_mask = df.ix[mask]
            length_data_mask = len(data_mask)
            data_as_matrix = np.asmatrix(data_mask)
            if length_data_mask > 0:
                for i in range(0, length_data_mask):
                    x3 = np.asarray(data_as_matrix[i])
                    x4 = x3[0, 0]
                    up1.append(x4)
                    # recursive function call
                    upstream_watershed(x4)

                return up1
            else:
                up2.append(-1)
                return up2

    upstream_watershed_id = upstream_watershed(num)
    return upstream_watershed_id
