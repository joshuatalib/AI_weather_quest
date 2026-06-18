# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from AI_WQ_package_EDITION2 import check_fc_submission
import ftplib
import os

def get_previous_monday(date_obj):
    if date_obj.weekday() != 0:  # Monday is 0
        prev_monday = date_obj - timedelta(days=date_obj.weekday())
        print(f"Warning: The date provided ({date_obj.date()}) is not a Monday.")
        print(f"Adjusting to the previous Monday: {prev_monday.date()}")
        choice = input("Do you want to continue with this adjusted date? (y/n): ").strip().lower()
        if choice != 'y':
            print("Operation aborted.")
            raise ValueError("Can only recieve historical observations for dates commencing on a Monday.")
        return prev_monday
    return date_obj

def change_lat_long_coord_names(da):
    da = da.rename({'lat':'latitude'})
    da = da.rename({'lon':'longitude'})
    return da
 
def ftp_or_ecbox_loading(remote_path,local_path,password):
    # EDITION 2 EDITS. Attempt with FTP and if fails, try with ecbox.
    # log onto FTP session
    try:
        session = ftplib.FTP('ftp.ecmwf.int', 'ai_weather_quest', password)

        with open(local_path, 'wb') as f:
            session.retrbinary(f"RETR {remote_path}", f.write)

        session.quit()
        print(f"Downloaded via FTP: {remote_path}")

    except ftplib.all_errors as ftp_error:
        print(f"FTP failed ({ftp_error}); trying ecbox instead")

        try:
            site = Site.from_space_and_name(space='ecbox', name='AI_Weather_Quest')
            site_auth = Authenticator.from_token(token=password)
            content_manager = site.get_content_manager(authenticator=site_auth)

            content = content_manager.download(remote_path=remote_path)
            with open(local_path, 'wb') as f:
                f.write(content)

            if not os.path.exists(local_path):
                raise RuntimeError("ecbox download did not create local file")

            print(f"Downloaded via ecbox: {remote_path}")

        except Exception as ecbox_error:
            raise RuntimeError(
                f"Both FTP and ecbox downloads failed for {remote_path}"
            ) from ecbox_error

def retrieve_land_sea_mask(password,local_destination=None):
    #### copy across 1.5 deg land sea mask used for evaluation ####
    # create a local filename ###
    if local_destination == None:
        local_filename = f'land_sea_mask_1pt5DEG.nc'
    else:
        local_filename = f'{local_destination}/land_sea_mask_1pt5DEG.nc'

    remote_path = f'land_sea_mask_1pt5DEG.nc'
    ftp_or_ecbox_loading(remote_path,local_filename,password)

    # open file using xarray.
    # when opening, drop the time coordinate from the xarray.
    land_sea_mask = xr.open_dataarray(local_filename).squeeze().reset_coords('time',drop=True)
    #land_sea_mask = change_lat_long_coord_names(land_sea_mask)
    # return the single day climatology.
    return land_sea_mask

def retrieve_20yr_quantile_clim(date,variable,password,local_destination=None):
    '''
    For Edition 2, changing function name to quantile climatology as introducing TS storm days terciles and MJO probabilities. All other variables, near-surface temperature, mean sea level pressure and precipitation remain as quintile probabilites.
    '''
    # get year of date variable. #######
    
    # check date input in valid
    check_fc_submission.is_valid_date(date)
    # get a data obj
    date_obj = datetime.strptime(date,'%Y%m%d')
    # check that the date obj is a Monday and if not, check that the user wants the previous Monday's data
    #date_obj = get_previous_monday(date_obj) # no longer need to check whether it is a Monday. Daily quintile climatologies are uploaded!
    date = datetime.strftime(date_obj,'%Y%m%d') # reload date in case it has changed

    # get the year component
    year = date_obj.year
    str_year = str(year)

    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr','MJO','TS'])

    # create local filename
    if variable == 'tas' or variable == 'mslp':
        filename = f'{variable}_20yrCLIM_WEEKLYMEAN_quintiles_{date}.nc'
    elif variable == 'pr':
        filename = f'{variable}_20yrCLIM_WEEKLYSUM_quintiles_{date}.nc'
    elif variable == 'TS': # added TS metric
        filename == '{variable}_20yrCLIM_WEEKLYTSDAYS_terciles_{date}.nc'

    if local_destination:
        local_filename = f'{local_destination}/{filename}'
    else:
        local_filename = filename

    remote_path = f'/climatologies/{str_year}/{filename}'

    ftp_or_ecbox_loading(remote_path,local_filename,password)

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
    # check that the date obj is a Monday and if not, check that the user wants the previous Monday's data
    date_obj = get_previous_monday(date_obj)
    date = datetime.strftime(date_obj,'%Y%m%d') # reload date in case it has changed

    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr','MJO','TS']) # Edition 2 includes MJO and TCfreq

    #### copy across single day climatological file ####
    # create a local filename ###
    if variable == 'tas' or variable == 'mslp':
        filename = f'{variable}_obs_WEEKLYMEAN_{date}.nc'
    elif variable == 'pr':
        filename = f'{variable}_obs_WEEKLYSUM_{date}.nc'
    elif variable == 'TS':
        filename = f'TSdays_obs_WEEKLYSUM_{date}.nc'
    elif variable == 'MJO':
        filename = f'{variable}_obs_DAILY_{date}.nc'

    if local_destination:
        local_filename = f'{local_destination}/{filename}'
    else:
        local_filename = filename

    remote_path = f'/observations/{date}/{filename}'

    ftp_or_ecbox_loading(remote_path,local_filename,password)

    # open file using xarray. # removes time bounds
    try:
        weekly_obs = xr.open_dataset(local_filename).squeeze().drop_dims('bnds').drop_vars('time_bnds',errors='ignore').to_array().squeeze()
    except:
        weekly_obs = xr.open_dataset(local_filename).squeeze().to_array().squeeze()
    # return the single day climatology.
    try: 
        weekly_obs = change_lat_long_coord_names(weekly_obs)
    except:
        pass
    return weekly_obs

def retrieve_all_period_fcdates(fc_init_date,password):
    local_filename = f'competition_dates_ED2_Aug25_Aug31.csv' # need to update competition dates file so it goes out further.
    remote_path = f'competition_dates_ED2_Aug25_Aug31.csv'
    ftp_or_ecbox_loading(remote_path,local_filename,password) 

    # use pandas to read the csv file. 
    df = pd.read_csv(local_filename)
    df['Start date'] = pd.to_datetime(df['Start date'],format='%A %d-%b-%Y %H:%M',errors='coerce')

    # split into thirteen week chunks
    chunk_size = 13
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

    # use the forecast date to check which 13-week period the initialisation date is in.
    target_date = pd.to_datetime(fc_init_date,format="%Y%m%d")

    # Find which chunk contains the target date
    for idx, chunk in enumerate(chunks):
        if target_date in chunk['Start date'].values:
            print(f"Target date found in chunk {idx+1}")
            period_dates = chunk

    # only collate dates where fc_init_date is smaller than or equal to Start date
    selected_period_dates = period_dates[period_dates['Start date'] <= fc_init_date]
    all_fc_init_dates = selected_period_dates['Start date'].dt.strftime('%Y%m%d').tolist()

    os.remove(local_filename) # once all initialisation dates have been extracted, remove the downloaded .csv file

    return all_fc_init_dates, idx # return all the fc init dates and idx of chunk

