rem cd C:\Users\dtarb\Code\RWDPreproRepo
rem PrepareRegions E:\NHDPlus

set RepoScriptDIR=C:\Users\dtarb\Code\RWDPreproRepo\
set RWDScriptDir=C:\Users\dtarb\Code\RWDScripts\
set PY27="C:\Python27\python.exe"
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set DataDir=%1



%PROPY% %RepoScriptDIR%NHD_PreProcessor5.py %DataDir% regionlist.txt 1

 