rem Inputs
Set FlowDir=%1
Set NHDFlowline=%2
Set NHDBurn=%3
Set DEM=%4
set gwstartno=%5

Rem Locations of codes
set RepoScriptDIR=%6
rem C:\Users\dtarb\Code\RWDPreproRepo\

set OtherScriptDIR=%7
rem C:\Users\dtarb\Code\RWDScripts\

Rem Python commands
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set PY27="C:\Python27\python.exe"

REM 
%PY27% %OtherScriptDIR%gdal_reclassify.py %FlowDir% fdr.tif -c "==1, ==2, ==4, ==8, ==16, ==32, ==64, ==128" -r "1, 8, 7, 6, 5, 4, 3, 2" -d 0 -n true 

Rem ArcGIS command to join burnevent features
Rem 
%PROPY% %RepoScriptDIR%join.py %NHDFlowline% temp.shp %NHDBurn% COMID Flowline.shp

Rem Dangle points 
Rem 
%PROPY% %RepoScriptDIR%verticesToDanglepoint.py %CD% Flowline.shp dangle.shp

Rem Dangle raster
Rem 
%PROPY% %RepoScriptDIR%pointtoraster.py  %CD% dangle.shp fdr.tif dangle.tif

Rem reclassify point raster 
Rem 
%PY27% %OtherScriptDIR%gdal_reclassify.py dangle.tif dangle_reclass.tif -c "==1" -r "1" -d 0 

Rem TauDEM functions

mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8.tif
mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8w.tif -wg dangle_reclass.tif -nc

rem  run threshold single processor.  There appears to be a problem with multiprocessor no data handling
mpiexec -n 1 threshold -ssa ad8w.tif -src src.tif -thresh 1

mpiexec -n 4 streamnet -fel %DEM% -p fdr.tif -ad8 ad8w.tif -src src.tif -ord ord.tif -tree tree.txt -coord coord.txt -net net.shp -w w.tif

mpiexec -n 4 D8HDistToStrm -p fdr.tif -src src.tif -dist dist.tif

rem For gridnet use mask so that gord is stream order
mpiexec -n 4 gridnet -p fdr.tif -plen plen.tif -tlen tlen.tif -gord gord.tif

rem  Run CatchOutlets single processor, no parallel version yet
mpiexec -n 1 CatchOutlets -net net.shp -p fdr.tif -o CatchOutlets3.shp -mindist 30000 -gwstartno %gwstartno%

mpiexec -n 4 gagewatershed -p fdr.tif -gw gw.tif -id id.txt -o CatchOutlets3.shp

Rem convert to polygons and dissolve
%PROPY% %RepoScriptDIR%rastertoPolygon.py  %CD% gw.tif gw_1.shp 
%PROPY% %RepoScriptDIR%dissolve.py  %CD% gw_1.shp gw.shp 



