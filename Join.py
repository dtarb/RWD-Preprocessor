import os
import sys

import arcpy


def main():
    """Join a table to a featureclass and select the desired attributes"""

    try:
        inFeatures = str(sys.argv[1])
        layerName = str(sys.argv[2])
        joinTable = str(sys.argv[3])
        joinField = str(sys.argv[4])
        outFeature = str(sys.argv[5])

        # Set environment settings
        arcpy.env.workspace = os.getcwd()
        arcpy.env.qualifiedFieldNames = False

        # Create a feature layer from the vegtype featureclass
        arcpy.MakeFeatureLayer_management(inFeatures,  layerName)

        # Join the feature layer to a table
        arcpy.AddJoin_management(layerName, joinField, joinTable, joinField, "KEEP_COMMON")

        # Copy the layer to a new permanent feature class
        arcpy.CopyFeatures_management(layerName, outFeature)

    except Exception as err:
            print(err.args[0])

if __name__ == "__main__":
    main()
