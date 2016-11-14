import shutil
import os
import sys
import subprocess
import glob

import fiona
from fiona import collection
import shapefile
from shapely.ops import cascaded_union
from shapely.geometry import shape, mapping
import numpy as np
import pandas as pd
from osgeo import ogr


from NHD_RWD_Utilities import complementary_gagewatershed, create_buffer

from DoMergeOGR import Do_Merge
# calling %PY27% %ScriptDIR%NHD_PreProcessor3.py %InputDir% regionlist.txt


def main(input_dir_name, regionlistfile):
   # regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
   # Read downids.  3 element lists with regionid, catchid, downid
   # make upidlist by second pass through appending downid
   # 3rd pass over catchments
   # If no catchments upstream watershed file is subwatershed file.  Flag as done
   # If there are catchments upstream
   #    go there recursively
   #    write subwatershed file
   #    write watershed file as merge of upstream watershed files
   masterIDfile = os.path.join(input_dir_name, "masterid.txt")
   downidlist=[]
   upidlist=[]
   catchdone=[]
   # Name subscripts for readibility
   reg=0
   catch=1
   downcatch=2
   with open(masterIDfile) as f:
       lines=f.read().splitlines()
   for x in lines:
       x1=[]
       for x2 in x.split():
           x1.append(int(x2))
       downidlist.append(x1)
   print (downidlist)
   for x in lines:
       x1=[]
       upidlist.append(x1)  # append empty list placeholders for upid's
       catchdone.append(False)
   ncatch=len(downidlist)
   for thiscatch in downidlist:
        if(thiscatch[downcatch] > 0):  # this catchment has a downid so record this catchment as this downid's upid
            upidlist[thiscatch[downcatch]-1].append(thiscatch[catch])  # use the -1 because indexing based in what is read from the files starts at 1
   print(upidlist)



# Define the recursive function
   def catchmerge(idtomerge):
       if not catchdone[idtomerge-1]:
           thiscatch=downidlist[idtomerge-1]
           listtomerge = [thiscatch[catch]]
           num = len(upidlist[thiscatch[catch] - 1])
           if (num > 0):
               for idup in upidlist[thiscatch[catch] - 1]:
                   catchmerge(idup)
                   listtomerge.append(idup)
           catchdone[idtomerge - 1]=True
           print(listtomerge)
           Do_Merge(input_dir_name, listtomerge)
   # Now we do the recursive pass
   for thiscatch in downidlist:
       num=len(upidlist[thiscatch[catch]-1])
       if(num > 0):
           for idup in upidlist[thiscatch[catch]-1]:
               catchmerge(idup)
       catchmerge(thiscatch[catch])
       print("done "+ str(thiscatch[catch]))
   print("done")


if __name__ == '__main__':
    main(*sys.argv[1:])



