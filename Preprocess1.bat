rem Inputs
Set FlowDir=%1
Set NHDFlowline=%2
Set NHDBurn=%3
Set DEM=%4
set gwstartno=%5

Rem Locations of codes
set RepoScriptDIR=%6
set OtherScriptDIR=%7

Rem Python commands
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set PY27="C:\Python27\python.exe"

%PY27% %OtherScriptDIR%gdal_reclassify.py %FlowDir% fdr.tif -c "==1, ==2, ==4, ==8, ==16, ==32, ==64, ==128" -r "1, 8, 7, 6, 5, 4, 3, 2" -d 0 -n true 

Rem ArcGIS command to join burnevent features
%PROPY% %RepoScriptDIR%join.py %NHDFlowline% temp.shp %NHDBurn% COMID Flowline.shp

Rem Dangle points 
%PROPY% %RepoScriptDIR%verticesToDanglepoint.py %CD% Flowline.shp dangle.shp

Rem Dangle raster
%PROPY% %RepoScriptDIR%pointtoraster.py  %CD% dangle.shp fdr.tif dangle.tif

Rem reclassify point raster 
%PY27% %OtherScriptDIR%gdal_reclassify.py dangle.tif dangle_reclass.tif -c "==1" -r "1" -d 0 

