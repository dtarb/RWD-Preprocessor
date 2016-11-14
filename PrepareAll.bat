set RepoScriptDIR=D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDPreproRepo\
set PY27="C:\Python2764\python.exe"
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set DataDir=%1

%PY27% %RepoScriptDIR%NHD_PreProcessor1.py %DataDir% regionlist.txt %RepoScriptDIR%Preprocess.bat 1

%PY27% %RepoScriptDIR%NHD_PreProcessor2.py %DataDir% regionlist.txt

%PY27% %RepoScriptDIR%NHD_PreProcessor3.py %DataDir% regionlist.txt

%PY27% %RepoScriptDIR%NHD_PreProcessor4.py %DataDir% regionlist.txt

%PROPY% %RepoScriptDIR%mosaicToRaster.py %DataDir% regionlist.txt
 