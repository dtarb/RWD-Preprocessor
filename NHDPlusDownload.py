import urllib
import os
import sys


def main(download_dir):
    with open(os.path.join(download_dir, 'RegionList.txt'), 'r') as f:
        lines = f.read().splitlines()
    regions = []
    # populate the regions list in this format:
    # [{'vpu': '08', 'rpus': ['08a', '08b', '03g']}]
    for line in lines[1:]:
        ls = line.split()
        subregions = []
        for sr in ls[1:]:
            subregions.append(sr)
        regions.append({'vpu': ls[0], 'rpus': subregions})

    region_area_ids = {'01': 'NE', '02': 'MA', '03N': 'SA', '03S': 'SA', '03W': 'SA', '04': 'GL', '05': 'MS',
                       '06': 'MS', '07': 'MS', '08': 'MS', '09': 'SR', '10L': 'MS', '10U': 'MS', '11': 'MS',
                       '12': 'TX', '13': 'RG', '14': 'CO', '15': 'CO', '16': 'GB', '17': 'PN', '18': 'CA',
                       '20': 'HI', '21': 'CI', '22AS': 'PI', '22GU': 'PI', '22MP': 'PI'}
    base_url = "ftp://www.horizon-systems.com/NHDPlus/NHDPlusV21/Data/NHDPlus{r_id}/"

    templates = []
    f = open(os.path.join(download_dir, "Files.txt"), 'w')
    fdr_file_name_template = "NHDPlusV21_{r_id}_{vpu}_{rpu}_FdrFac_{vn}.7z"
    dem_file_name_template = "NHDPlusV21_{r_id}_{vpu}_{rpu}_Hydrodem_{vn}.7z"
    burn_file_name_template = "NHDPlusV21_{r_id}_{vpu}_NHDPlusBurnComponents_{vn}.7z"
    snap_file_name_template = "NHDPlusV21_{r_id}_{vpu}_NHDSnapshot_{vn}.7z"
    templates.append(fdr_file_name_template)
    templates.append(dem_file_name_template)
    templates.append(burn_file_name_template)
    templates.append(snap_file_name_template)
    testfile = urllib.URLopener()
    for region_dict in regions:
        for rpu in region_dict['rpus']:
            for template in templates:
                for vn in range(1, 100):
                    # download file version number (vn)
                    # we are trying version number 1 to 99
                    if vn < 10:
                        vn = "0" + str(vn)
                    else:
                        vn = str(vn)
                    file_name = template.format(r_id=region_area_ids[region_dict['vpu']],  vpu=region_dict['vpu'],
                                                rpu=rpu, vn=vn)
                    file_url = "NHDPlus{vpu}".format(vpu=region_dict['vpu']) + "/" + file_name
                    file_url = base_url.format(r_id=region_area_ids[region_dict['vpu']]) + file_url
                    if not os.path.isfile(os.path.join(download_dir, file_name)):
                        if not url_exists(file_url):
                            continue
                        try:
                            print ("Trying " + file_name)
                            testfile.retrieve(file_url, os.path.join(download_dir, file_name))
                            if os.path.isfile(os.path.join(download_dir, file_name)):
                                print ("File download success:{}".format(file_name))
                                f.write(file_name + "\n")
                            else:
                                print ("File download did not create file:{}".format(file_name))
                        except Exception as ex:
                            print ("File download failed:{}".format(file_name))
                            print (ex.message)
                        break
                    else:
                        break
    f.close()


def url_exists(url):
    try:
        urllib.urlopen(url)
    except Exception:
        return False
    return True

if __name__ == "__main__":
    main(*sys.argv[1:])
