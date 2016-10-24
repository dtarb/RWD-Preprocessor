# Name: FeatureVerticesToPoints_Example2.py
# Description: Use FeatureVerticesToPoints function to get the mid-points
#              of input line features

 

# import system modules
import sys
import arcpy
from arcpy import env

def verticesToStartpoint (datadir,Infeature,OutFeature):
    # Set environment settings
    env.workspace = datadir
     
    # Set local variables
    inFeatures = Infeature
    outFeatureClass = env.workspace +"/"+ OutFeature

    # Execute FeatureVerticesToPoints
    arcpy.FeatureVerticesToPoints_management(inFeatures, outFeatureClass, "START")

    
if __name__ == '__main__':
    datadir = sys.argv[1]
    Infeature = sys.argv[2]
    OutFeature=sys.argv[3]

    verticesToStartpoint (datadir,Infeature,OutFeature)



