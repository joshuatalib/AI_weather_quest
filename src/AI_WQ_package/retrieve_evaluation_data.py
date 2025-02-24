# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from AI_WQ_package import check_fc_submission
import ftplib

def change_lat_long_coord_names(da):
    da = da.rename({'lat':'latitude'})
    da = da.rename({'lon':'longitude'})
    return da

def retrieve_land_sea_mask(password,local_destination=None):
    #### copy across 1.5 deg land sea mask used for evaluation ####
    # create a local filename ###
    if local_destination == None:
        local_filename = f'land_sea_mask_1pt5DEG.nc'
    else:
        local_filename = f'{local_destination}/land_sea_mask_1pt5DEG.nc'

    # log onto FTP session
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password)
    remote_path = f'land_sea_mask_1pt5DEG.nc'
    # retrieve the full year file 
    with open(local_filename,'wb') as f:
        session.retrbinary(f"RETR {remote_path}", f.write)

    print(f"File '{remote_path}' has been downloaded to successfully.")

    session.quit()
    # downloaded single climatological file #### 
    # open file using xarray.
    # when opening, drop the time coordinate from the xarray.
    land_sea_mask = xr.open_dataarray(local_filename).squeeze().reset_coords('time',drop=True)
    #land_sea_mask = change_lat_long_coord_names(land_sea_mask)
    # return the single day climatology.
    return land_sea_mask

def retrieve_20yr_quintile_clim(date,variable,password,local_destination=None):
    '''
    '''
    # get year of date variable. #######
    
    # check date input in valid
    check_fc_submission.is_valid_date(date)
    # get a data obj
    date_obj = datetime.strptime(date,'%Y%m%d')
    # get the year component
    year = date_obj.year
    str_year = str(year)

    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr'])

    #### copy across single day climatological file ####
    # create a local filename ###
    if local_destination == None:
        local_filename = f'{variable}_20yrCLIM_WEEKLYMEAN_quintiles_{date}.nc'
    else:
        local_filename = f'{local_destination}/{variable}_20yrCLIM_WEEKLYMEAN_quintiles_{date}.nc'

    # log onto FTP session
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password) 
    if variable == 'tas' or variable == 'mslp':
        remote_path = f'/climatologies/{str_year}/{variable}_20yrCLIM_WEEKLYMEAN_quintiles_{date}.nc'
    elif variable == 'pr':
        remote_path = f'/climatologies/{str_year}/{variable}_20yrCLIM_WEEKLYSUM_quintiles_{date}.nc'
    # retrieve the full year file 
    with open(local_filename,'wb') as f:
        session.retrbinary(f"RETR {remote_path}", f.write)
  
    print(f"File '{remote_path}' has been downloaded to successfully.")

    session.quit()
    # downloaded single climatological file #### 
    # open file using xarray.
    single_day_clim = xr.open_dataarray(local_filename).squeeze()
    try: 
         single_day_clim = change_lat_long_coord_names(single_day_clim)
    except:
        pass
    # return the single day climatology.
    return single_day_clim

def retrieve_weekly_obs(date,variable,password,local_destination=None):
    '''
    date = date of observational week
    '''
    # check date input in valid
    check_fc_submission.is_valid_date(date)
    # get a data obj
    date_obj = datetime.strptime(date,'%Y%m%d')

    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr'])

    #### copy across single day climatological file ####
    # create a local filename ###
    if variable == 'tas' or variable == 'mslp':
        if local_destination == None:
            local_filename = f'{variable}_obs_WEEKLYMEAN_{date}.nc'
        else:
            local_filename = f'{local_destination}/{variable}_obs_WEEKLYMEAN_{date}.nc'
    elif variable == 'pr':
        if local_destination == None:
            local_filename = f'{variable}_obs_WEEKLYSUM_{date}.nc'
        else:
            local_filename = f'{local_destination}/{variable}_obs_WEEKLYSUM_{date}.nc'

    # log onto FTP session
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password)
    if variable == 'tas' or variable == 'mslp':
        remote_path = f'/observations/{date}/{variable}_obs_WEEKLYMEAN_{date}.nc'
    elif variable == 'pr':
        remote_path = f'/observations/{date}/{variable}_obs_WEEKLYSUM_{date}.nc'
    
    # retrieve the full year file 
    with open(local_filename,'wb') as f:
        session.retrbinary(f"RETR {remote_path}", f.write)

    print(f"File '{remote_path}' has been downloaded to successfully.")

    session.quit()
    # open file using xarray. # removes time bounds
    weekly_obs = xr.open_dataset(local_filename).squeeze().drop_dims('bnds').drop_vars('time_bnds',errors='ignore').to_array().squeeze()
    # return the single day climatology.
    try: 
        weekly_obs = change_lat_long_coord_names(weekly_obs)
    except:
        pass
    return weekly_obs

