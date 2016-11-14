REM This script takes its arguments as the directory of the region folder where it should be run and the start number for catchments

rem Inputs
Set FlowDir=fdr.tif
Set NHDFlowline=NHDFlowline.shp
Set NHDBurn=BurnLineEvent.dbf
Set DEM=dem.tif
rem set InputDir=%1
rem D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\NHDPlus\cd1\reg8
set gwstartno=%1

Rem Locations of codes
rem Set RepoScriptDIR=%3
set RepoScriptDIR=D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDPreproRepo\

rem Set OtherScriptDIR=%4
set OtherScriptDIR=D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDScripts\

rem set PROPY=%5
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

rem set PY27=%6
set PY27="C:\Python2764\python.exe"


REM cd %InputDir%
rem 
mkdir Main_Watershed

REM Note that the default python is 2.7
REM 
%PY27% %OtherScriptDIR%gdal_reclassify.py fdr.tif Main_Watershed\fdr.tif -c "==1, ==2, ==4, ==8, ==16, ==32, ==64, ==128" -r "1, 8, 7, 6, 5, 4, 3, 2" -d 0 -n true 

Rem ArcGIS command to join burnevent features
Rem 
%PROPY% %RepoScriptDIR%join.py %NHDFlowline% temp.shp %NHDBurn% COMID Main_Watershed\Flowline.shp

Rem Dangle points 
Rem 
%PROPY% %RepoScriptDIR%verticesToDanglepoint.py Main_Watershed Flowline.shp dangle.shp

Rem Dangle raster
Rem 
%PROPY% %RepoScriptDIR%pointtoraster.py  Main_Watershed dangle.shp fdr.tif dangle.tif

Rem reclassify point raster 
Rem 
%PY27% %OtherScriptDIR%gdal_reclassify.py Main_Watershed\dangle.tif Main_Watershed\dangle_reclass.tif -c "==1" -r "1" -d 0 

Rem TauDEM functions
cd Main_Watershed
rem 
mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8.tif -nc
rem 
mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8w.tif -wg dangle_reclass.tif -nc
rem  run threshold single processor.  There appears to be a problem with multiprocessor no data handling
mpiexec -n 1 threshold -ssa ad8w.tif -src src.tif -thresh 1
rem 
mpiexec -n 4 streamnet -fel ..\dem.tif -p fdr.tif -ad8 ad8.tif -src src.tif -ord ord.tif -tree tree.txt -coord coord.txt -net net.shp -w w.tif
rem 
mpiexec -n 4 D8HDistToStrm -p fdr.tif -src src.tif -dist dist.tif
rem 
mpiexec -n 4 gridnet -p fdr.tif -plen plen.tif -tlen tlen.tif -gord gord.tif
rem 
mpiexec -n 1 %OtherScriptDIR%CatchOutlets -net net.shp -p fdr.tif -o CatchOutlets3.shp -mindist 30000 -gwstartno %gwstartno%
rem 
mpiexec -n 4 %OtherScriptDIR%gagewatershed -p fdr.tif -gw gw.tif -id id.txt -o CatchOutlets3.shp
cd ..

Rem convert to polygons and dissolve
rem 
%PROPY% %RepoScriptDIR%rastertoPolygon.py  Main_Watershed gw.tif gw_1.shp
rem 
%PROPY% %RepoScriptDIR%dissolve.py  Main_Watershed gw_1.shp gw.shp 



