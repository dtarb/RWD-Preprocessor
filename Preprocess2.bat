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

Rem TauDEM functions

Rem With edge contamination checks to use in reporting catchment areas
Rem mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8.tif

Rem  Without edge contamination checks to use in delineating stream network for partitioning
Rem mpiexec -n 4 aread8 -p fdr.tif -ad8 ad81.tif -nc

Rem  With dangle points as weight to seed delineation close to NHD mapped streams
Rem mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8w.tif -wg dangle_reclass.tif -nc

rem  run threshold single processor.  There appears to be a problem with multiprocessor no data handling
Rem mpiexec -n 1 threshold -ssa ad8w.tif -src src.tif -thresh 1
rem  Threshold of 1000 is 0.9 km^2.  Smaller self draining areas will be left out
Rem mpiexec -n 1 threshold -ssa ad81.tif -src src1.tif -thresh 1000

Rem mpiexec -n 4 streamnet -fel %DEM% -p fdr.tif -ad8 ad81.tif -src src1.tif -ord ord1.tif -tree tree1.txt -coord coord1.txt -net net1.shp -w w1.tif

Rem mpiexec -n 4 D8HDistToStrm -p fdr.tif -src src.tif -dist dist.tif

rem  The only quantity used from this first result is plen so that basin length is the longest path from the divide
Rem mpiexec -n 4 gridnet -p fdr.tif -plen plen.tif -tlen tlen1.tif -gord gord.tif
rem  Repeat gridnet with src as mask for stream order and tlen to report.  Tlen here is total length upstream on the stream raster so proper for drainage density.
Rem mpiexec -n 4 gridnet -p fdr.tif -plen plen1.tif -tlen tlen.tif -gord ord.tif -mask src.tif -thresh 1

rem  Run CatchOutlets single processor, no parallel version yet
Rem mpiexec -n 1 CatchOutlets -net net1.shp -p fdr.tif -o CatchOutlets3.shp -mindist 20000 -minarea 50000000 -gwstartno %gwstartno%

Rem mpiexec -n 4 gagewatershed -p fdr.tif -gw gw.tif -id id.txt -o CatchOutlets3.shp

Rem convert to polygons and dissolve
%PROPY% %RepoScriptDIR%rastertoPolygon.py  %CD% gw.tif gw_1.shp 
%PROPY% %RepoScriptDIR%dissolve.py  %CD% gw_1.shp gw.shp 



