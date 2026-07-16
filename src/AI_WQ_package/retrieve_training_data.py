# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from AI_WQ_package import check_fc_submission, retrieve_evaluation_data
import ftplib

def get_basin_domain(basin,format360=False):
    if basin == 'ATL':
        if format360:
            lon_bounds=[260.0,340.0]
        else:
            lon_bounds=[-100.0,-20.0]
        lat_bounds=[0.0,40.0]
    elif basin == 'NEP':
        if format360:
            lon_bounds=[180.0,220.0]
        else:
            lon_bounds=[-180.0,-140.0]
        lat_bounds=[0.0,40.0]
    elif basin == 'NWP':
        lon_bounds=[100.0,180.0]
        lat_bounds=[0.0,40.0]
    elif basin == 'NIN':
        lon_bounds=[45.0,100.0]
        lat_bounds=[0.0,40.0]
    elif basin == 'SWIO':
        lon_bounds=[20.0,90.0]
        lat_bounds=[-40.0,0.0]
    elif basin == 'SEIO':
        lon_bounds=[90.0,160.0]
        lat_bounds=[-40.0,0.0]
    elif basin == 'SPac':
        if format360:
            lon_bounds=[160.0,240.0]
        else:
            lon_bounds=[(160.0, 180.0), (-180.0, -120.0)] # two slice approach
        lat_bounds=[-40.0,0.0]
    return lat_bounds, lon_bounds

def retrieve_annual_training_data(year,variable,password,local_destination=None):
    '''
    year = year of training dataset
    '''
    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr','MJO','TS'])

    # NEED TO CHECK YEAR IS BETWEEN 1979 TO (YEAR OF CURRENT DATE - FOUR MONTHS)
    if variable != 'TS':
        month_delay = 4
    else:
        month_delay = 12

    latency_date = datetime.now() - relativedelta(months=month_delay)
    latency_date_YEAR = latency_date.year
    if not (1979 <= year <= latency_date_YEAR):
        raise ValueError(f"Invalid year: {year}. Year must be between 1979 and {latency_date_YEAR}.")

    #### copy across single day climatological file ####
    # create a local filename ###
    if variable == 'tas' or variable == 'mslp':
        filename = f'{variable}_sevenday_WEEKLYMEAN_{year}.nc'
    elif variable == 'pr':
        filename = f'{variable}_sevenday_WEEKLYSUM_{year}.nc'
    elif variable == 'TS':
        filename = f'{variable}_sevenday_WEEKLYTSDAYS_{year}.nc'
    elif variable == 'MJO':
        filename = f'MJO_DAILY_{year}.nc'

    if local_destination:
        local_filename = f'{local_destination}/{filename}'
    else:
        local_filename = filename

    remote_path = f'/training_data/{filename}'

    retrieve_evaluation_data.ftp_or_ecbox_loading(remote_path,local_filename,password)
    
    # open file using xarray. # removes time bounds
    full_year_obs = xr.open_dataset(local_filename).squeeze()
    return full_year_obs
