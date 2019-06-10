### This repository contains Python script for Sentinel-1 image pre-processing using snappy. 

1. Before running the code, you need to install the [Sentinel Toolbox Application (SNAP)](https://step.esa.int/main/download/snap-download/) and [configure Python to use the SNAP-Python (snappy) interface](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface)

2. The code read in unzipped Sentinel-1 GRD products (EW and IW modes).
    - Sentinel-1 images can be downloaded from:
      - [Sentinels Scientific Data Hub](https://scihub.copernicus.eu/dhus/#/home)  or
      - [Alaska Satellite Facility](https://vertex.daac.asf.alaska.edu/#)
3. Sentinel-1 pre-processing steps:
    
    - Apply orbit file
    - GRD border noise removal
    - Thermal noise removal
    - Radiometric calibration
    - Speckle filtering
    - Terrain correction
    - Subset

   
   This is the general pre-processing steps for Sentinel-1. Since each step is written in separate function, it can be cutomized based on user needs.
   IW images are downsampled from 10m to 40m (the same resolution as EW images) in the terrain correction step.

### Support

Please reach out to me at wajuqi@gmail.com.
