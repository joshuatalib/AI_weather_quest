# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from AI_WQ_package import check_fc_submission
import ftplib

def retrieve_annual_training_data(year,variable,password,local_destination=None):
    '''
    year = year of training dataset
    '''
    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr'])

    # NEED TO CHECK YEAR IS BETWEEN 1979 TO 2024
    if not (1979 <= year <= 2024):
        raise ValueError(f"Invalid year: {year}. Year must be between 1979 and 2024.")

    #### copy across single day climatological file ####
    # create a local filename ###
    if variable == 'tas' or variable == 'mslp':
        # add details of local destination if given
        if local_destination == None:
            local_filename = f'{variable}_sevenday_WEEKLYMEAN_{year}.nc'
        else:
            local_filename = f'{local_destination}/{variable}_sevenday_WEEKLYMEAN_{year}.nc'
    elif variable == 'pr':
        if local_destination == None:
            local_filename = f'{variable}_sevenday_WEEKLYSUM_{year}.nc'
        else:
            local_filename = f'{local_destination}/{variable}_sevenday_WEEKLYSUM_{year}.nc'

    # log onto FTP session
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password)
    if local_destination == None:
        remote_path = f'/training_data/{local_filename}'
    else:
        if variable == 'tas' or variable == 'mslp':
            remote_path = f'/training_data/{variable}_sevenday_WEEKLYMEAN_{year}.nc'
        elif variable == 'pr':
            remote_path = f'/training_data/{variable}_sevenday_WEEKLYSUM_{year}.nc'
    
    # retrieve the full year file 
    with open(local_filename,'wb') as f:
        session.retrbinary(f"RETR {remote_path}", f.write)

    print(f"File '{remote_path}' has been downloaded to successfully to '{local_filename}'.")

    session.quit()
    # open file using xarray. # removes time bounds
    full_year_obs = xr.open_dataset(local_filename).squeeze()
    return full_year_obs

