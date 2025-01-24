# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from AI_WQ_package import check_fc_submission
import ftplib

def retrieve_annual_training_data(year,variable,password):
    '''
    year = year of training dataset
    '''
    # check variable is valid
    check_fc_submission.check_variable_in_list(variable,['tas','mslp','pr'])

    # NEED TO CHECK YEAR IS BETWEEN 1979 TO 2024

    #### copy across single day climatological file ####
    # create a local filename ###
    if variable == 'tas' or variable == 'mslp':
        local_filename = f'{variable}_sevenday_WEEKLYMEAN_{year}.nc'
    elif variable == 'pr':
        local_filename = f'{variable}_sevenday_WEEKLYSUM_{year}.nc'

    # log onto FTP session
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password)
    remote_path = f'/training_data/{local_filename}'
    # retrieve the full year file 
    with open(local_filename,'wb') as f:
        session.retrbinary(f"RETR {remote_path}", f.write)

    print(f"File '{remote_path}' has been downloaded to successfully.")

    session.quit()
    # open file using xarray. # removes time bounds
    full_year_obs = xr.open_dataset(local_filename).squeeze()
    return full_year_obs

