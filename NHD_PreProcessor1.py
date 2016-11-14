import shutil
import os
import sys
import subprocess


def main(input_dir_name, regionlistfile,batfile,FirstCatchid):

    regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    regionfolders = [region.strip() for region in regions]

    catchId=FirstCatchid
    for workname in regionfolders:
        workfolder = os.path.join(input_dir_name,workname)
        batname = os.path.basename(batfile)
        shutil.copy(batfile,workfolder)  # Clumsy but could not sort out paths to this
        os.chdir(workfolder)  # Change to work folder and run therein
        runbat = batname + " " + str(catchId)
        subprocess.check_call(runbat)
        gageIDfile = os.path.join(workfolder, "Main_Watershed", "id.txt")
        dataall=[]
        with open(gageIDfile) as f:
            lines = f.read().splitlines()
        for e in lines[1:]:
            x1 = []  # id as a list
            for x in e.split():
                x1.append(int(x))
            dataall.append(x1)
        ncatch=len(dataall)

        # increment catchid for next time round
        catchId=dataall[ncatch-1][0]
        print("Done " + workname + " from " + str(dataall[0][0]) + " to " + str(catchId))
        catchId = catchId + 1

if __name__ == '__main__':
    main(*sys.argv[1:])



