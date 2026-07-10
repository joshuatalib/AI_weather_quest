#!/usr/bin/env python
import cdsapi
import sys
import calendar
from datetime import datetime
import subprocess
import os

## script to download ERA5 daily data for AI weather quest competition 
# 1.0 grid, reg grid. preferable to save netcdf
GRID="1.0/1.0"

VARIABLE=sys.argv[1]
VAR_NAME=sys.argv[2]
YEAR_START=int(sys.argv[3])
YEAR_END=int(sys.argv[4])

TIME="00:00:00/06:00:00/12:00:00/18:00:00"

c = cdsapi.Client()

# go through year and month.
# for each month, create a string of date.
for year in range(YEAR_START,YEAR_END+1):
    for month in range(1,3):
        # Determine the number of days in the month
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

        days_in_month = calendar.monthrange(year, month)[1]
        dates = ",".join([f"{year}-{month:02d}-{day:02d}" for day in range(1, days_in_month + 1)])

        # Create a request file for MARS
        grib_file = f"ERA5_sfc_{year}_{month:02d}_inst_{VARIABLE}.grib"
        nc_file = f"ERA5_sfc_{year}_{month:02d}_inst_{VARIABLE}.nc"
        daymean_file = f"ERA5_sfc_{year}_{month:02d}_inst_{VARIABLE}_DAYMEAN.nc"
        print(f"Downloading data for {VARIABLE}, {year}-{month:02d}...")
    
        c.retrieve(
                         "reanalysis-era5-single-levels",
                {
                "product_type": "reanalysis",
                "format": "grib",
                "variable": f"{VARIABLE}",
                "date": f"{start_date}/{end_date}",
                "time": f"{TIME}",
                "grid": f"{GRID}",
                },
                grib_file,)

        # Convert GRIB to NetCDF
        print(f"Converting {grib_file} to NetCDF...")
        subprocess.run(["cdo", "-f", "nc", "copy", grib_file, nc_file], check=True)
        # Compute daily mean
        print(f"Computing daily mean for {nc_file}...")
        subprocess.run(["cdo", "daymean", nc_file, daymean_file], check=True)

        # Remove intermediate GRIB and NetCDF files
        #os.remove(grib_file)
        #os.remove(nc_file)

    # Merge all daily files into one annual file
    annual_file = f"{VAR_NAME}_DAYMEAN_{year}.nc"
    print(f"Merging daily files into annual file: {annual_file}...")
    subprocess.run(
            ["cdo", "mergetime", f"ERA5_sfc_{year}_*_inst_{VARIABLE}_DAYMEAN.nc", annual_file],
            check=True,
    )

    # Remove all intermediate daily files
    #for file in os.listdir(DIR):
    #    if file.startswith(f"ERA5_sfc_{year}_") and file.endswith("_DAYMEAN.nc"):
    #        os.remove(os.path.join(DIR, file))
