# Name: FeatureVerticesToPoints_Example2.py
# Description: Use FeatureVerticesToPoints function to get the mid-points
#              of input line features

 
# import system modules
import sys
import arcpy
from arcpy import env

def verticesToDanglepoint (datadir,Infeature,OutFeature):
    # Set environment settings
    env.workspace = datadir
     
    # Set local variables
    inFeatures = Infeature
    outFeatureClass = env.workspace +"/"+ OutFeature

    # Execute FeatureVerticesToPoints
    arcpy.FeatureVerticesToPoints_management(inFeatures, outFeatureClass, "DANGLE")

    fieldName1 = "Gval"
    fieldPrecision = 4
     
    # Execute AddField twice for two new fields
    arcpy.AddField_management(outFeatureClass, fieldName1, "SHORT", fieldPrecision, "", "",
                              "", "NULLABLE")
    arcpy.CalculateField_management(outFeatureClass, fieldName1, 
                                        "1", "PYTHON_9.3")
if __name__ == '__main__':
    datadir = sys.argv[1]
    Infeature = sys.argv[2]
    OutFeature=sys.argv[3]

    verticesToDanglepoint (datadir,Infeature,OutFeature)


