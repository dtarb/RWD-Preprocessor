import os
import sys

import arcpy
from arcpy import env


def main(datadir, infeature, outfeature):
    """get the start-points of input line features"""

    # Set environment settings
    env.workspace = datadir
     
    # Set local variables
    infeatures = infeature
    outfeature_class = os.path.join(env.workspace, outfeature)

    # Execute FeatureVerticesToPoints
    arcpy.FeatureVerticesToPoints_management(infeatures, outfeature_class, "START")

    
if __name__ == '__main__':
    datadir = sys.argv[1]
    infeature = sys.argv[2]
    outfeature = sys.argv[3]

    main(datadir, infeature, outfeature)



