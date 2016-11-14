import shutil
import os
import sys
import subprocess
import fiona

from NHD_RWD_Utilities import create_buffer

def main(input_dir_name, regionlistfile):

    regions = open(os.path.join(input_dir_name, regionlistfile), 'r')
    regionfolders = [region.strip() for region in regions]

    masterIDfile = os.path.join(input_dir_name, "masterid.txt")
    catchidlist=[]
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
       catchidlist.append(x1)
    print (catchidlist)
    ncatch=len(catchidlist)

    infile=os.path.join(input_dir_name, "gwmaster.shp")
    for thiscatch in catchidlist:
        swfolder = os.path.join(input_dir_name, "Subwatershed_ALL", "Subwatershed%s" % thiscatch[catch])
        swfile = os.path.join(swfolder,"subwatershed_%s.shp" % thiscatch[catch])
        tempfolder = os.path.join(swfolder,"temp")
        if not os.path.exists(tempfolder):
            os.mkdir(tempfolder)
        bufferfile = os.path.join(tempfolder,"buffer.shp")

        # creating buffer shape file
        buffer_distance = 120  # 4 30 m grid cells for NHD
        create_buffer(swfile, bufferfile, buffer_distance)

        reg_dir = os.path.join(input_dir_name,regionfolders[thiscatch[reg]])
        flow_in_file = os.path.join(reg_dir,"Main_Watershed","fdr.tif")
        stream_in_file = os.path.join(reg_dir,"Main_Watershed","src.tif")
        distance_in_file = os.path.join(reg_dir,"Main_Watershed","dist.tif")
        ad8_in_file = os.path.join(reg_dir,"Main_Watershed","dist.tif")
        plen_in_file = os.path.join(reg_dir,"Main_Watershed","plen.tif")
        tlen_in_file = os.path.join(reg_dir,"Main_Watershed","tlen.tif")
        gord_in_file = os.path.join(reg_dir,"Main_Watershed","gord.tif")
        flow_out_file = os.path.join(swfolder, 'subwatershed_%sp.tif' % thiscatch[catch])
        stream_out_file = os.path.join(swfolder, 'subwatershed_%ssrc1.tif' % thiscatch[catch])
        distance_out_file = os.path.join(swfolder, 'subwatershed_%sdist.tif' % thiscatch[catch])
        ad8_out_file = os.path.join(swfolder, 'subwatershed_%sad8.tif' % thiscatch[catch])
        plen_out_file = os.path.join(swfolder, 'subwatershed_%splen.tif' % thiscatch[catch])
        tlen_out_file = os.path.join(swfolder, 'subwatershed_%stlen.tif' % thiscatch[catch])
        gord_out_file = os.path.join(swfolder, 'subwatershed_%sgord.tif' % thiscatch[catch])

        input = fiona.open(bufferfile, 'r')
        xmin = str(input.bounds[0])
        ymin = str(input.bounds[1])
        xmax = str(input.bounds[2])
        ymax = str(input.bounds[3])
        layer_name = os.path.basename(bufferfile)
        layer_name = os.path.splitext(layer_name)[0]
        input.close()

        command_flow = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                       " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                       flow_in_file + " " + flow_out_file
        command_stream = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                         " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                         stream_in_file + " " + stream_out_file
        command_distance = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                           " -dstnodata -32768.00 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                           distance_in_file+ " " + distance_out_file

        command_ad8 = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                      " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                      ad8_in_file+ " " + ad8_out_file
        command_plen = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                       " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                       plen_in_file + " " + plen_out_file
        command_tlen = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                       " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                       tlen_in_file + " " + tlen_out_file
        command_gord = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                       " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                       gord_in_file + " " + gord_out_file

        subprocess.check_call(command_flow)
        subprocess.check_call(command_stream)
        subprocess.check_call(command_distance)

        subprocess.check_call(command_ad8)
        subprocess.check_call(command_plen)
        subprocess.check_call(command_tlen)
        subprocess.check_call(command_gord)
        shutil.rmtree(tempfolder, ignore_errors=True)
    print("Done")



if __name__ == '__main__':
    main(*sys.argv[1:])



