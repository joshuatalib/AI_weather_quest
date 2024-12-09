# python code that will accept quintile, lat, long data and submit forecast to FTP site
import xarray as xr
import numpy as np
import ftplib
import os
#import sys
#sys.path.append('/perm/ecm0847/S2S_comp/AI_WEATHER_QUEST_code/AI_weather_quest/src/AI_WQ_package/')
from AI_WQ_package import check_fc_submission

def create_ftp_dir_if_does_not_exist(ftp,dir_name):
    """
    Create a directory on the FTP server only if it doesn't exist.
    
    Parameters:
        ftp (ftplib.FTP): The FTP connection object.
        dir_name (str): The name of the directory to create.
    """
    try:
        # Try to list the directory
        ftp.cwd(dir_name)
        print(f"Directory '{dir_name}' already exists.")
    except ftplib.error_perm as e:
        # If directory doesn't exist (Permission error), create it
        if "550" in str(e):  # "550" is the FTP error code for "directory not found"
            ftp.mkd(dir_name)
            print(f"Directory '{dir_name}' created.")
        else:
            # Raise if the error is something else (not directory not found)
            raise

def AI_WQ_create_empty_dataarray(variable,fc_start_date,fc_period,teamname,modelname):
    ''' Function that creates an 'empty' dataarray that will support forecast submission.
    The AI WQ advises users to download the empty dataarray and then fill it with their forecasted values.
    The function is also used during forecast submission to ensure all participants submit the same file.
    '''

    # standard for all variables
    standard_names_all_vars = {'units':'1','grid_mapping':'hcrs','coordinates':'latitude longitude'}

    # set standard names of variable
    if variable == 'mslp':
        data_specs = {**{'standard_name':'air_pressure_at_sea_level'},**standard_names_all_vars}
    elif variable == 'tas':
        data_specs = {**{'standard_name':'air_temperature'},**standard_names_all_vars}
    elif variable == 'pr':
        data_specs = {**{'standard_name':'precipitation'},**standard_names_all_vars}

    fc_issue_date = fc_start_date[:4]+'-'+fc_start_date[4:6]+'-'+fc_start_date[6:]

    # empty data
    empty_data = np.empty((5,181,360))

    # dimension attributes
    lat_attrs = {'units':'degrees_north','long_name':'latitude','standard_name':'latitude','axis':'X'}
    lon_attrs = {'units':'degrees_east','long_name':'longitude','standard_name':'longitude','axis':'Y'}
    time_attrs = {'standard_name': 'forecast_reference_time','long_name': 'reference time','axis':'T'}
    latitude = np.arange(90.0,-91.0,-1.0)
    longitude = np.arange(0.0,360.0,1.0)

    # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
    da = xr.DataArray(data=empty_data,dims=['quintile','latitude','longitude'],
            coords=dict(quintile=(['quintile'],np.arange(0.2,1.1,0.2)), # outputs [0.2,0.4,0.6,0.8,1.0]
                        latitude=(['latitude'],latitude,lat_attrs),
                        longitude=(['longitude'],longitude,lon_attrs),
                        time=np.datetime64(fc_issue_date+'T00:00:00')),
            attrs=dict(**data_specs,description=variable+' prediction from '+teamname+' using '+modelname,Conventions='CF-1.6'))
    # finally, add the time attrs
    da.coords['time'].attrs = time_attrs

    return da

def AI_WQ_forecast_submission(data,variable,fc_start_date,fc_period,teamname,modelname,checks=True):
    ''' This function will take a dataset in quintile, lat, long format, save as appropriate netCDF format,
    then copy to FTP site under correct forecast folder, i.e. 20241118. 

    Parameters:
        data (xarray.Dataset): xarray dataset with forecasted probabilites in format (quintile, lat, long). 
        variable (str): Saved variable. Options include 'tas', 'mslp' and 'pr'.
        fc_start_date (str): The forecast start date as a string in format '%Y%m%d', i.e. 20241118.
        fc_period (str or number): Either forecast period 1 (days 18 to 24) for forecast period 2 (days 25 to 31).
        teamname (str): The teamname that was submitted during registration.
        modelname (str): Modelname for particular forecast. Teams are only allowed to submit three models each.

    '''
    ###############################################################################################################
    # CHECKING DATA FORMAT AND INPUTTED VARIABLES
    # outputs the data (dataarray) and final filename
    data, final_filename = check_fc_submission.all_checks(data,variable,fc_start_date,fc_period,teamname,modelname)

    data_only = data.values # this should be shaped, quintile, latitude, longitude.

    submitted_da = AI_WQ_create_empty_dataarray(variable,fc_start_date,fc_period,teamname,modelname)
    submitted_da.values = data_only

    submitted_da.to_netcdf(final_filename) # save netcdf file temporaily whether the script is being run
    
    ################################################################################################################
    
    # save new dataset as netCDF to FTP site
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest','NegF8LfwK') # open FTP session
    create_ftp_dir_if_does_not_exist(session,'forecast_submissions/'+fc_start_date) # save the forecast directory if it does not exist
    remote_path = f"/forecast_submissions/{fc_start_date}/{final_filename}"
    print (remote_path)

    file = open(final_filename,'rb') # read the forecast file
    
    # as of 6th Dec 2024 - couldn't rewrite over old files so delete if already existing
    try:
        session.delete(remote_path)
        print(f"Existing file '{final_filename}' deleted.")
    except ftplib.error_perm:
        pass
    session.storbinary(f'STOR {remote_path}',file) # transfer to FTP site
    file.close() # close the file and quit the session
    session.quit()

    os.remove(final_filename) # delete the saved dataarray.
    
    return submitted_da



