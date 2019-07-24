# Need to configure Python to use the SNAP-Python (snappy) interface(https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface)
# Read in unzipped Sentinel-1 GRD products (EW and IW modes)
# Parameters to provide: path, outpath, region_code

import datetime
import time
from snappy import ProductIO
from snappy import HashMap
import os, gc
from snappy import GPF

def do_apply_orbit_file(source):
    print('\tApply orbit file...')
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    output = GPF.createProduct('Apply-Orbit-File', parameters, source)
    return output

def do_remove_GRD_border_noise(source):
    print('\tGRD border noise removal...')
    parameters = HashMap()
    parameters.put('Remove-GRD-Border-Noise', True)
    output = GPF.createProduct('Remove-GRD-Border-Noise', parameters, source)
    return output

def do_thermal_noise_removal(source):
    print('\tThermal noise removal...')
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    output = GPF.createProduct('ThermalNoiseRemoval', parameters, source)
    return output

def do_calibration(source, polarization, pols):
    print('\tCalibration...')
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    if polarization == 'DH':
        parameters.put('sourceBands', 'Intensity_HH,Intensity_HV')
    elif polarization == 'DV':
        parameters.put('sourceBands', 'Intensity_VH,Intensity_VV')
    elif polarization == 'SH' or polarization == 'HH':
        parameters.put('sourceBands', 'Intensity_HH')
    elif polarization == 'SV':
        parameters.put('sourceBands', 'Intensity_VV')
    else:
        print("different polarization!")
    parameters.put('selectedPolarisations', pols)
    parameters.put('outputImageScaleInDb', False)
    output = GPF.createProduct("Calibration", parameters, source)
    return output

def do_speckle_filtering(source):
    print('\tSpeckle filtering...')
    parameters = HashMap()
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    output = GPF.createProduct('Speckle-Filter', parameters, source)
    return output

def do_terrain_correction(source, proj, downsample):
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'GETASSE30')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', proj)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
    parameters.put('saveProjectedLocalIncidenceAngle', True)
    parameters.put('saveSelectedSourceBand', True)
    while downsample == 1:                      # downsample: 1 -- need downsample to 40m, 0 -- no need to downsample
        parameters.put('pixelSpacingInMeter', 40.0)
        break
    output = GPF.createProduct('Terrain-Correction', parameters, source)
    return output

def do_subset(source, wkt):
    print('\tSubsetting...')
    parameters = HashMap()
    parameters.put('geoRegion', wkt)
    output = GPF.createProduct('Subset', parameters, source)
    return output

def main():
    ## All Sentinel-1 data sub folders are located within a super folder (make sure the data is already unzipped and each sub folder name ends with '.SAFE'):
    path = r'data\s1_images'
    outpath = r'data\s1_preprocessed'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    ## well-known-text (WKT) file for subsetting (can be obtained from SNAP by drawing a polygon)
    wkt = 'POLYGON ((-157.79579162597656 71.36872100830078, -155.4447021484375 71.36872100830078, \
    -155.4447021484375 70.60020446777344, -157.79579162597656 70.60020446777344, -157.79579162597656 71.36872100830078))'
    ## UTM projection parameters
    proj = '''PROJCS["UTM Zone 4 / World Geodetic System 1984",GEOGCS["World Geodetic System 1984",DATUM["World Geodetic System 1984",SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],UNIT["degree", 0.017453292519943295],AXIS["Geodetic longitude", EAST],AXIS["Geodetic latitude", NORTH]],PROJECTION["Transverse_Mercator"],PARAMETER["central_meridian", -159.0],PARAMETER["latitude_of_origin", 0.0],PARAMETER["scale_factor", 0.9996],PARAMETER["false_easting", 500000.0],PARAMETER["false_northing", 0.0],UNIT["m", 1.0],AXIS["Easting", EAST],AXIS["Northing", NORTH]]'''

    for folder in os.listdir(path):
        gc.enable()
        gc.collect()
        sentinel_1 = ProductIO.readProduct(path + "\\" + folder + "\\manifest.safe")
        print(sentinel_1)

        loopstarttime=str(datetime.datetime.now())
        print('Start time:', loopstarttime)
        start_time = time.time()

        ## Extract mode, product type, and polarizations from filename
        modestamp = folder.split("_")[1]
        productstamp = folder.split("_")[2]
        polstamp = folder.split("_")[3]

        polarization = polstamp[2:4]
        if polarization == 'DV':
            pols = 'VH,VV'
        elif polarization == 'DH':
            pols = 'HH,HV'
        elif polarization == 'SH' or polarization == 'HH':
            pols = 'HH'
        elif polarization == 'SV':
            pols = 'VV'
        else:
            print("Polarization error!")

        ## Start preprocessing:
        applyorbit = do_apply_orbit_file(sentinel_1)
        bordernoise = do_remove_GRD_border_noise(applyorbit)
        thermaremoved = do_thermal_noise_removal(bordernoise)
        calibrated = do_calibration(thermaremoved, polarization, pols)
        down_filtered = do_speckle_filtering(calibrated)
        del applyorbit
        del bordernoise
        del thermaremoved
        del calibrated
        ## IW images are downsampled from 10m to 40m (the same resolution as EW images).
        if (modestamp == 'IW' and productstamp == 'GRDH') or (modestamp == 'EW' and productstamp == 'GRDH'):
            down_tercorrected = do_terrain_correction(down_filtered, proj, 1)
            down_subset = do_subset(down_tercorrected, wkt)
            del down_filtered
            del down_tercorrected
        elif modestamp == 'EW' and productstamp == 'GRDM':
            tercorrected = do_terrain_correction(down_filtered, proj, 0)
            subset = do_subset(tercorrected, wkt)
            del down_filtered
            del tercorrected
        else:
            print("Different spatial resolution is found.")

        down = 1
        try: down_subset
        except NameError:
            down = None
        if down is None:
            print("Writing...")
            ProductIO.writeProduct(subset, outpath + '\\' + folder[:-5], 'GeoTIFF')
            del subset
        elif down == 1:
            print("Writing undersampled image...")
            ProductIO.writeProduct(down_subset, outpath + '\\' + folder[:-5] + '_40', 'GeoTIFF')
            del down_subset
        else:
            print("Error.")

        print('Done.')
        sentinel_1.dispose()
        sentinel_1.closeIO()
        print("--- %s seconds ---" % (time.time() - start_time))

if __name__== "__main__":
    main()
