set RepoScriptDIR=D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDPreproRepo\
set RWDScriptDir=D:\Dropbox\Projects\MMW2_StroudWPenn\RWDWork\Code\RWDScripts\
set PY27="C:\Python27\python.exe"
set PROPY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set DataDir=%1

%PY27% %RepoScriptDIR%NHD_PreProcessor1.py %DataDir% regionlist.txt %RepoScriptDIR% 1 %RepoScriptDIR% %RWDScriptDir%

%PY27% %RepoScriptDIR%NHD_PreProcessor2.py %DataDir% regionlist.txt

%PROPY% %RepoScriptDIR%NHD_PreProcessor3.py %DataDir% regionlist.txt

 