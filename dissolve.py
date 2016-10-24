import os
import sys

import arcpy


def main(datadir, layername, outfeature):
    """ Dissolve features based on common attributes"""

    arcpy.env.workspace = datadir
     
    # Set local variables
    temp_layer = layername

    outfeature_class = os.path.join(datadir, outfeature)
    dissolve_fields = ["GRIDCODE"]

    # Execute Dissolve using LANDUSE and TAXCODE as Dissolve Fields
    arcpy.Dissolve_management(temp_layer, outfeature_class, dissolve_fields, "",
                              "MULTI_PART", "DISSOLVE_LINES")

if __name__ == '__main__':
    datadir = sys.argv[1]
    layername = sys.argv[2]
    outfeature = sys.argv[3]

    main(datadir, layername, outfeature)


