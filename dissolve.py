# Name: Dissolve_Example2.py
# Description: Dissolve features based on common attributes

 
# Import system modules
import sys
import arcpy

def dissolve(datadir,layername,Infeature,Outfeature):
    arcpy.env.workspace = datadir
     
    # Set local variables
    inFeatures = Infeature
    tempLayer = layername
    #expression = arcpy.AddFieldDelimiters(inFeatures, "LANDUSE") + " <> ''"
    outFeatureClass = datadir+"/"+Outfeature
    dissolveFields = ["GRIDCODE"]
     
    # Execute MakeFeatureLayer and SelectLayerByAttribute.  This is only to exclude 
    #  features that are not desired in the output.
   # arcpy.MakeFeatureLayer_management(inFeatures, tempLayer)
   # arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION", expression)
     
    # Execute Dissolve using LANDUSE and TAXCODE as Dissolve Fields
    arcpy.Dissolve_management(tempLayer, outFeatureClass, dissolveFields, "", 
                              "MULTI_PART", "DISSOLVE_LINES")

if __name__ == '__main__':
    datadir = sys.argv[1]
    layername=sys.argv[2]
    Infeature = sys.argv[3]
    OutFeature=sys.argv[4]

    dissolve(datadir,layername,Infeature,OutFeature)


