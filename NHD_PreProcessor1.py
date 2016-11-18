import shutil
import os
import sys
import subprocess
import fiona

from NHD_RWD_Utilities import complementary_gagewatershed, create_buffer, read_regionlist, read_gageids


def main(input_dir_name, regionlistfile,batfile,FirstCatchid,Repodir,Scriptdir):

    (regions, subregions, regionfolders) = read_regionlist(input_dir_name, regionlistfile)

    # Name subscripts for readibility
    reg = 0
    catch = 1
    downcatch = 2

    maxId = int(FirstCatchid)-1
    RWDdir = os.path.join(input_dir_name, "RWDData")
    if not os.path.exists(RWDdir):  # If RWDdir does not yet exist create it
        os.mkdir(RWDdir)
    Regdir=os.path.join(input_dir_name,"Regions")
    if not os.path.exists(Regdir):  # If Regions folder does not yet exist create it
        os.mkdir(Regdir)

    for ireg in xrange(len(regionfolders)):
        workname = regionfolders[ireg]
        region=regions[ireg]
        subregion=subregions[ireg]
        workfolder = os.path.join(input_dir_name,"Regions",workname)
        if os.path.exists(workfolder):  # Here the region folder exists so scan the id.txt file to get max number for next processing
            dataall = read_gageids(os.path.join(workfolder, "id.txt"))
            ncatch = len(dataall)
            maxId = max(dataall[ncatch - 1][0],maxId)

    # Here we have done a parse over any folders present and determined the maxId of subcatchments already extracted
    # Now we do this again, but for unprocessed regions

    for ireg in xrange(len(regionfolders)):
        workname = regionfolders[ireg]
        region = regions[ireg]
        subregion = subregions[ireg]
        workfolder = os.path.join(input_dir_name, "Regions", workname)
        if not os.path.exists(workfolder):  # Here the region folder needs to be created and processed
            os.mkdir(workfolder)
            catchId = maxId + 1  # Get a new catchId to start from

            Flowdir=os.path.join(input_dir_name,"NHDPlusMS","NHDPlus"+region,"NHDPlusFdrFac"+subregion,"fdr")
            NHDFlowline = os.path.join(input_dir_name,"NHDPlusMS","NHDPlus"+region,"NHDSnapshot","Hydrography","NHDFlowline.shp")
            NHDBurn = os.path.join(input_dir_name,"NHDPlusMS","NHDPlus"+region,"NHDPlusBurnComponents","BurnLineEvent.dbf")
            DEM =os.path.join(input_dir_name,"NHDPlusMS","NHDPlus"+region,"NHDPlusHydrodem"+subregion,"hydrodem")
            batname = os.path.basename(batfile)
            shutil.copy(batfile,workfolder)  # Clumsy but could not sort out paths to this
            os.chdir(workfolder)  # Change to work folder and run therein
            runbat = batname + " " + Flowdir + " " + NHDFlowline + " " + NHDBurn + " " + DEM + " " + str(catchId) + " " + Repodir + " " + Scriptdir
            subprocess.check_call(runbat)

            # Now the terrain analysis processing is done
            dataall = read_gageids(os.path.join(workfolder, "id.txt"))
            ncatch=len(dataall)
            maxId = max(dataall[ncatch - 1][0], maxId)

            #  Make subcatchment folders and write single shapefiles
            infile = os.path.join(workfolder, "gw.shp")
            dest = os.path.join(RWDdir, "Subwatershed_ALL")
            if not os.path.exists(dest):
                os.mkdir(dest)
            with fiona.open(infile) as source:
                sink_schema = source.schema.copy()
                # for types and example refer to http://toblerity.org/fiona/manual.html
                sink_schema['properties']['mergefield'] = 'int'  # Set a field value of 1 for all shapes to facilitate dissolving later
                for f in source:
                    thiscatch=int(f['properties']['GRIDCODE'])
                    swfolder = os.path.join(dest, "Subwatershed%s" % thiscatch)
                    if os.path.exists(swfolder):  # delete folder if it was there.  We have already parsed the existing regions and got the max of numbers we needed so and folder with this number remaining is no longer needed
                        shutil.rmtree(swfolder, ignore_errors=True)
                    os.mkdir(swfolder)
                    swfile = os.path.join(swfolder, "subwatershed_%s.shp" % thiscatch)
                    with fiona.open(swfile, 'w', crs=source.crs, driver=source.driver,schema=sink_schema) as sink:
                        f['properties'].update(mergefield=int(1))
                        sink.write(f)
                        # print(int(f['properties']['GRIDCODE']))
                        sink.close()

                    tempfolder = os.path.join(swfolder, "temp")
                    if not os.path.exists(tempfolder):
                        os.mkdir(tempfolder)
                    bufferfile = os.path.join(tempfolder, "buffer.shp")

                    # creating buffer shape file
                    buffer_distance = 120  # 4 30 m grid cells for NHD
                    create_buffer(swfile, bufferfile, buffer_distance)

                    flow_in_file = os.path.join(workfolder, "fdr.tif")
                    stream_in_file = os.path.join(workfolder, "src.tif")
                    distance_in_file = os.path.join(workfolder, "dist.tif")
                    ad8_in_file = os.path.join(workfolder, "ad8.tif")
                    plen_in_file = os.path.join(workfolder, "plen.tif")
                    tlen_in_file = os.path.join(workfolder, "tlen.tif")
                    ord_in_file = os.path.join(workfolder, "ord.tif")
                    flow_out_file = os.path.join(swfolder, 'subwatershed_%sp.tif' % thiscatch)
                    stream_out_file = os.path.join(swfolder, 'subwatershed_%ssrc1.tif' % thiscatch)
                    distance_out_file = os.path.join(swfolder, 'subwatershed_%sdist.tif' % thiscatch)
                    ad8_out_file = os.path.join(swfolder, 'subwatershed_%sad8.tif' % thiscatch)
                    plen_out_file = os.path.join(swfolder, 'subwatershed_%splen.tif' % thiscatch)
                    tlen_out_file = os.path.join(swfolder, 'subwatershed_%stlen.tif' % thiscatch)
                    ord_out_file = os.path.join(swfolder, 'subwatershed_%sord.tif' % thiscatch)

                    with fiona.open(bufferfile,'r') as input:
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
                                       distance_in_file + " " + distance_out_file
                    command_ad8 = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                                  " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                                  ad8_in_file + " " + ad8_out_file
                    command_plen = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                                   " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                                   plen_in_file + " " + plen_out_file
                    command_tlen = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                                   " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                                   tlen_in_file + " " + tlen_out_file
                    command_ord = "gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + \
                                   " -dstnodata -32768 -cutline " + bufferfile + " -cl " + layer_name + " " + \
                                   ord_in_file + " " + ord_out_file

                    subprocess.check_call(command_flow)
                    subprocess.check_call(command_stream)
                    subprocess.check_call(command_distance)

                    subprocess.check_call(command_ad8)
                    subprocess.check_call(command_plen)
                    subprocess.check_call(command_tlen)
                    subprocess.check_call(command_ord)
                    shutil.rmtree(tempfolder, ignore_errors=True)
                source.close()

        print("Done " + workname + " from " + str(dataall[0][0]) + " to " + str(dataall[ncatch - 1][0]))
    print("Done Extraction phase")


if __name__ == '__main__':
    main(*sys.argv[1:])



