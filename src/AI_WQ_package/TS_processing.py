# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

# python script that computes tercile-based climatology of TS days
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from AI_WQ_package import forecast_submission, retrieve_training_data, plotting_forecast
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys

def single_basin(basin,full_dataset,return_mask=False):
    # get basin domain, and cut out storms
    lat_bounds, lon_bounds = retrieve_training_data.get_basin_domain(basin)
    # --- longitude mask ---
    if isinstance(lon_bounds[0], tuple):
        # multiple longitude slices (dateline-crossing basin)
        lon_mask = False
        for lo, hi in lon_bounds:
            lon_mask = lon_mask | ((full_dataset.lon >= lo) & (full_dataset.lon <= hi))
    else:
        # single continuous longitude range
        lon_mask = ((full_dataset.lon >= lon_bounds[0]) & (full_dataset.lon <= lon_bounds[1]))

    # --- latitude mask ---
    lat_mask = ((full_dataset.lat >= lat_bounds[0]) & (full_dataset.lat <= lat_bounds[1]))

    storms = full_dataset.where(lon_mask & lat_mask,drop=True)
    if return_mask:
        mask = lon_mask & lat_mask
        return mask
    else:
        return storms

def download_IBTRACS_compute_TStercile_climatology(date_str,ibtracs_filename,savedir):
    full_dataset = download_IBTRACS(ibtracs_filename)
    compute_20yr_TStercile_climatology(date_str, full_dataset, savedir) # compute the climatology

def download_IBTRACS(ibtracs_filename):
    dataset = xr.open_dataset(ibtracs_filename,engine='netcdf4',decode_coords=True,chunks={"storm":500})
    # remove all unnecesssary variables
    for data_var in dataset.data_vars:
        if data_var not in ['usa_wind','wmo_wind','season','number']:
            dataset = dataset.drop_vars(data_var)
    dataset = dataset.compute()
    return dataset

def count_nstormdays(storms_single_basin, start, end, basin):

    mask = ((storms_single_basin['time'] >= start) &
            (storms_single_basin['time'] <  end))
    storms_filtered = storms_single_basin.where(mask, drop=True)

    n_valid_storms = storms_filtered.sizes.get('storm', 0)
    if n_valid_storms == 0:
        return 0

    times = storms_filtered['time'].dt.floor('D')
    times_int = times.values.astype('int64')
    times_date = times.values
    storm_ids = storms_filtered['storm'].values

    # Broadcast IDs
    storm_ids_2d = np.broadcast_to(storm_ids[:, None], times_int.shape)

    # Validity masks
    not_nan = np.isfinite(times_date)
    in_window = ((times_date >= start) & (times_date < end))
    TS_level = storms_filtered['usa_wind'] >= 33.0454
    wind_valid = np.isfinite(storms_filtered['usa_wind'])
    loc_mask = single_basin(basin, storms_filtered, return_mask=True)

    valid = not_nan & in_window & TS_level & wind_valid & loc_mask

    pairs = np.unique(
        np.stack([storm_ids_2d[valid], times_int[valid]], axis=1),
        axis=0
    )

    return pairs.shape[0]

def compute_20yr_TStercile_climatology(date_str, ibtracs, savedir):
    """
    date_str = YYYYMMDD date format to compute tercile climatology
    ibtracs: IBRACS filename on local system.
    """
    
    print (f'Computing Tropical Storm Day terciles for {date_str}')
    
    date = datetime.strptime(date_str,'%Y%m%d')
    
    # reduce number of years for quick processing (stuck to 21 and 0 in case of overlap into previous year, i.e. Dec to Jan)
    fc_year = date.year
    lower_year = fc_year-21
    upper_year = fc_year

    storms = ibtracs.copy()
    storms['lon'] = ((storms['lon'] + 180) % 360) - 180

    storms = storms.where(storms['time'].dt.year >= lower_year,drop=True)
    storms = storms.where(storms['time'].dt.year <= upper_year,drop=True)

    print (f"full IBTRACS dataset loaded")

    # set empty arrays
    lower_terciles_nstormdays = []
    upper_terciles_nstormdays = []
    
    for basin in ['ATL','NWP','SWIO','SEIO']:
        print (f"Calculating for basin {basin}")
        # get basin domain, and cut out storms
        storms_single_basin = single_basin(basin,storms)
        # storms must have a wind greater than 17 m s-1 or 33 kts. recorded by US agency
        storms_single_basin = storms_single_basin.where(storms_single_basin['usa_wind'].notnull() & (storms_single_basin['usa_wind'] >= 33.0454),drop=True)

        count_nstormdays_in_week = []
        # loop through climatology previous 20 years, +/- 4 days
        for year_diff in range(-20,0): # year diff
            for day_diff in [-4,-2,0,2,4]: # day diff
                print (f"computing for year lag {year_diff}, day lag {day_diff}")
                # get start date of week for chosen year
                lagged_date = date + relativedelta(years=year_diff) + relativedelta(days=day_diff)
    
                # get start and end day of appropriate week
                lagged_datetime_start = np.datetime64(lagged_date)
                lagged_datetime_end = np.datetime64(lagged_date + relativedelta(days=7))

                nstorm_days = count_nstormdays(storms_single_basin, lagged_datetime_start, lagged_datetime_end, basin)
                count_nstormdays_in_week.append(nstorm_days)
        
        count_nstormdays_in_week = np.asarray(count_nstormdays_in_week)
    
        lower_terciles_nstormdays.append(np.percentile(count_nstormdays_in_week,1/3*100.0))
        upper_terciles_nstormdays.append(np.percentile(count_nstormdays_in_week,2/3*100.0))
    
    lower_tercile_nstormdays = np.asarray(lower_terciles_nstormdays)
    upper_tercile_nstormdays = np.asarray(upper_terciles_nstormdays)
    
    # populate tercile probability xarray, (tercile, domain)
    # add shortName
    shortName = 'TS'
    # dimension attributes
    basin_attrs = {'long_name':'Oceanic basin','standard_name':'Basin'}
    # work out forecast issue time
    date_iso = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    single_time = np.datetime64(date_iso + "T00:00:00")
    da = xr.DataArray(data=[lower_tercile_nstormdays,upper_tercile_nstormdays],dims=['tercile','basin'],
                    coords=dict(tercile=(['tercile'],np.arange(1,3)/3), # outputs [0.3333,0.6666]
                                basin=(['basin'],['ATL','NWP','SWIO','SEIO'],basin_attrs),
                                valid_time=single_time
                                ),
                    attrs=dict(Conventions='CF-1.6',shortName=shortName,units='tercile_bounds_storm_days_per_week'))
    da.to_netcdf(f"{savedir}/TS_20yrCLIM_WEEKLYTSDAYS_terciles_{date_str}.nc") # save the file

def compute_single_week_numTSdays(date_str,ibtracs):
    print (f'Computing number tropical storm days for {date_str}')

    date = datetime.strptime(date_str,'%Y%m%d')

    # convert all longitudes so they are -180 to 180.0
    # copy ibtracs in function
    storms = ibtracs.copy()
    storms['lon'] = ((storms['lon'] + 180) % 360) - 180

    print (f"full IBTRACS dataset loaded")

    # set empty arrays
    nstormdays = []

    for basin in ['ATL','NWP','SWIO','SEIO']:
        print (f"Calculating for basin {basin}")
        # get basin domain, and cut out storms
        storms_single_basin = single_basin(basin,storms)
        # storms must have a wind greater than 17 m s-1 or 33 kts. recorded by US agency
        storms_single_basin = storms_single_basin.where(storms_single_basin['usa_wind'].notnull() & (storms_single_basin['usa_wind'] >= 33.0454),drop=True)

        # get start and end day of appropriate week
        date_start = np.datetime64(date)
        date_end = np.datetime64(date_start + relativedelta(days=7))

        nstorm_days = count_nstormdays(storms_single_basin, date_start, date_end, basin)
        nstormdays.append(nstorm_days)

    nstormdays = np.asarray(nstormdays)

    # populate tercile probability xarray, (tercile, basin)
    # add shortName
    shortName = 'TS'
    # dimension attributes
    basin_attrs = {'long_name':'Oceanic basin','standard_name':'Basin'}
    # work out forecast issue time
    date_iso = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    single_time = np.datetime64(date_iso + "T00:00:00")
    numTSdays = xr.DataArray(data=nstormdays[None,:],dims=['time','basin'],
                    coords=dict(time=[single_time],
                                basin=(['basin'],['ATL','NWP','SWIO','SEIO'],basin_attrs),
                                ),
                    attrs=dict(Conventions='CF-1.6',shortName=shortName,units='storm_days_per_week'))

    return numTSdays

