REM Execute this script in directory where data is being assembled (e.g. C:\Users\dtarb\RWD_reg8b)

Set ScriptDIR=C:\Users\dtarb\RWDScript\
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

REM 
mkdir Main_Watershed

REM Note that the default python is Anaconda 2.7
REM 
python %ScriptDIR%gdal_reclassify.py NHDPlusMS\NHDPlus08\NHDPlusFdrFac08b\fdr Main_Watershed\fdr.tif -c "==1, ==2, ==4, ==8, ==16, ==32, ==64, ==128" -r "1, 8, 7, 6, 5, 4, 3, 2" -d 0 -n true 

Rem ArcGIS command to join burnevent features
Rem 
%PROPY% %ScriptDIR%join.py NHDPlusMS\NHDPlus08\NHDSnapshot\Hydrography\NHDFlowline.shp NHDFlowline.shp NHDPlusMS\NHDPlus08\NHDPlusBurnComponents\BurnLineEvent.dbf COMID Main_Watershed\Flowline.shp

Rem Dangle points 
Rem 
%PROPY% %ScriptDIR%verticesToDanglepoint.py Main_Watershed Flowline.shp dangle.shp

Rem Dangle raster
Rem 
%PROPY% %ScriptDIR%pointtoraster.py  Main_Watershed dangle.shp fdr.tif dangle.tif

Rem reclassify point raster 
Rem 
python %ScriptDIR%gdal_reclassify.py Main_Watershed\dangle.tif Main_Watershed\dangle_reclass.tif -c "==1" -r "1" -d 0 

Rem TauDEM functions
cd Main_Watershed
rem 
mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8.tif -nc
rem 
mpiexec -n 4 aread8 -p fdr.tif -ad8 ad8w.tif -wg dangle_reclass.tif -nc
rem 
mpiexec -n 4 threshold -ssa ad8w.tif -src src.tif -thresh 1
rem 
mpiexec -n 4 streamnet -fel C:\Users\dtarb\RWD_reg8b\NHDPlusMS\NHDPlus08\NHDPlusHydrodem08b\hydrodem -p fdr.tif -ad8 ad8w.tif -src src.tif -ord ord.tif -tree ree.txt -coord coord.txt -net net.shp -w w.tif
rem 
mpiexec -n 4 D8HDistToStrm -p fdr.tif -src src.tif -dist dist.tif
rem 
mpiexec -n 4 gridnet -p fdr.tif -plen plen.tif -tlen tlen.tif -gord gord.tif
rem 
mpiexec -n 1 CatchOutlets -net net.shp -p fdr.tif -o CatchOutlets3.shp -mindist 15000
rem 
mpiexec -n 4 gagewatershed -p fdr.tif -gw gw.tif -id id.txt -o CatchOutlets.shp
cd ..

Rem convert to polygons and dissolve
rem 
%PROPY% %ScriptDIR%rastertoPolygon.py  Main_Watershed gw.tif gw_1.shp
rem 
%PROPY% %ScriptDIR%dissolve.py  Main_Watershed gw_1.shp gw.shp

rem
python %ScriptDIR%NHD_PreProcessor_For_Rapid_Watershed_Delineation.py C:\Users\dtarb\RWD_reg8b gw.shp id.txt fdr.tif src.tif dist.tif ad8.tif plen.tif tlen.tif gord.tif 


