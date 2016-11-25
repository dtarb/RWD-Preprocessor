import os
import glob
import zipfile

groupsize=1000  # target 1000
files=glob.glob("gw*")
print(files)
zf=zipfile.ZipFile("rwdMS.zip","w",allowZip64 = True)
for file in files:
    zf.write(file)
zf.write("masterid.txt")
zf.close()
files = glob.glob("Subwatershed_ALL/*")
print (files)
nfiles=len(files)
ngroups=nfiles/groupsize+1
for i in range(ngroups):
    zipname="MSsub%s.zip" % int(i+1)
    zf=zipfile.ZipFile(zipname,"w",allowZip64 = True)
    firstingroup=i*groupsize
    lastingroup=min(firstingroup+groupsize,nfiles)
    groupfiles=files[firstingroup:lastingroup]
    for file in groupfiles:
        subfiles=glob.glob(os.path.join(file,"*"))
        for f in subfiles:
            zf.write(f)
    zf.close()
    print("Group %s done" % str(i+1))
print("Done")
# cmd="C:\Program Files\7-Zip\7z.exe" a rwddata.zip m*

# os.system(cmd)