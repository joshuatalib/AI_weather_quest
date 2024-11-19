# python code that will accept quintile, lat, long data and submit forecast to FTP site
import xarray as xr
import numpy as np
import ftplib

def check_variable_in_list(variable_name, expected_values):
    if variable_name not in expected_values:
        raise ValueError(f"Expected one of {expected_values}, but got {variable_name}.")

def convert_wk_lead_time_to_string(value):
    # convert the wk_lead_time variable to a string for saving
    if isinstance(value,(int,float)):
        return str(int(value)) # save a string of the integer value
    elif isinstance(value,(str)):
        return value # if it already is a string, just return the string value
    else:
        raise ValueError(f"The value '{value}' is not a number nor str.")

def check_string_is_in_file(filepath,string):
    with open(filepath,'r') as file:
        file_contents = file.read()
    if string not in file_contents:
        raise ValueError(f"{string} is not in list of acceptable submissions.")

def check_and_flip_latitudes(ds, lat_name='latitude'):
    """
    Check if latitudes range from 90 to -90, and flip if necessary.

    Parameters:
        ds (xarray.Dataset): The dataset to check.
        lat_name (str): Name of the latitude variable in the dataset.

    Returns:
        xarray.Dataset: The modified dataset with corrected latitude ordering. Latitude ordering should always be 90 to -90.
    """
    # Check if the latitude variable exists
    if lat_name not in ds.coords:
        raise ValueError(f"Latitude coordinate '{lat_name}' not found in the dataset.")

    # Extract latitude values
    latitudes = ds[lat_name].values

    # Check if latitudes need to be flipped
    if latitudes[0] < latitudes[-1]:  # If increasing order
        print("Latitudes are in ascending order; flipping them to descend from 90 to -90.")
        ds = ds.sortby(lat_name, ascending=False)
    return ds

def check_and_convert_longitudes(ds, lon_name='longitude'):
    """
    Check if longitudes range from 0 to 360 and convert if necessary.

    Parameters:
        ds (xarray.Dataset): The dataset to check.
        lon_name (str): Name of the longitude variable in the dataset.

    Returns:
        xarray.Dataset: The modified dataset with longitudes converted to 0 to 360 range.
    """
    # Check if the longitude variable exists
    if lon_name not in ds.coords:
        raise ValueError(f"Longitude coordinate '{lon_name}' not found in the dataset.")

    # Extract longitude values
    longitudes = ds[lon_name].values

    # Check if longitudes are in the -180 to 180 range
    if np.any(longitudes < 0):
        print("Longitudes are in the -180 to 180 range; converting to 0 to 360.")
        longitudes = (longitudes + 360) % 360  # Convert to 0 to 360 range
        ds = ds.assign_coords({lon_name: longitudes})  # Update the dataset's longitude coordinates
    return ds

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

def AI_WQ_forecast_submission(data,variable,fc_start_date,wk_lead_time,teamname,modelname):
    ''' This function will take a dataset in quintile, lat, long format, save as appropriate netCDF format,
    then copy to FTP site under correct forecast folder, i.e. 20241118. 

    Parameters:
        data (xarray.Dataset): xarray dataset with forecasted probabilites in format (quintile, lat, long). 
        variable (str): Saved variable. Options include 'tas', 'mslp' and 'pr'.
        fc_start_date (str): The forecast start date as a string in format '%Y%m%d', i.e. 20241118.
        wk_lead_time (str or number): Three- or four-week forecast, i.e. '3' or 3.
        teamname (str): The teamname that was submitted during registration.
        modelname (str): Modelname for particular forecast. Teams are only allowed to submit three models each.

    '''
    ###############################################################################################################
    # CHECKING DATA FORMAT AND INPUTTED VARIABLES

    # Check all submitted variables are correct format.
    check_variable_in_list(variable,['tas','mslp','pr'])
    #check_string_is_in_file('mondays_start_dates.txt',fc_start_date) # checking whether forecast start date is a Monday and in correct format
    
    # check_variable_in_list(teamname,[]) # to be updated, check that teamname is in list of registered teamnames.

    # if wk_lead_time is number, change to string.
    wk_lead_time_str = convert_wk_lead_time_to_string(wk_lead_time)
    check_variable_in_list(wk_lead_time_str,['3','4']) # then check wk_lead_time is either string of 3 or 4.

    # after all checks have been performed regarding filename, save final finalname
    final_filename = variable+'_'+fc_start_date+'_wk'+wk_lead_time_str+'_'+teamname+'_'+modelname+'.nc'

    ################################################################################################################
    # OPEN NETCDF DATA AND INPUT INTO NEW netCDF xarray

    # first perform some checks on xarray
    # (1) latitudes should be 90.0 to -90.0
    data = check_and_flip_latitudes(data)
    # (2) longitudes should be 0 to 359.0
    data = check_and_convert_longitudes(data)

    # get data variable key and extract values
    data_var_key = list(data.data_vars.keys())[0]
    data_only = data[data_var_key].values # this should be shaped, quintile, latitude, longitude

    # define coordinates
    lat_coord = ('latitude',np.arange(90.0,-91.0,-1.0),{'units':'degrees_north','long_name':'latitude','standard_name':'latitude','axis':'X'})
    lon_coord = ('longitude',np.arange(0.0,360.0,1.0),{'units':'degrees_east','long_name':'longitude','standard_name':'longitude','axis':'Y'})
    quintile_coord = ('quintile',np.arange(0.2,1.1,0.2))

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

    # add a reference time coordinate
    reference_time = ('reftime', np.array([fc_issue_date+'T00:00:00'], dtype='datetime64[ns]'), {
    'units': 'seconds since 1980-01-01T00:00:00',
    'calendar': 'gregorian',
    'standard_name': 'forecast_reference_time',
    'long_name': 'reference time',
    'axis':'T'})

    # need to add weekly-mean characteristic. 

    # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
    ds = xr.Dataset(
            data_vars={variable:(['quintile','latitude','longitude'],data_only,data_specs)
                },
            coords=dict(quintile=quintile_coord, # outputs [0.2,0.4,0.6,0.8,1.0]
                        latitude=lat_coord,
                        longitude=lon_coord,
                        time=reference_time),
            attrs=dict(description=variable+' prediction from '+teamname+' using '+modelname+' at week '+wk_lead_time_str+' lead time',Conventions='CF-1.6'))

    ds.to_netcdf(final_filename) # save netcdf file temporaily whether the script is being run
    
    ################################################################################################################
    
    # save new dataset as netCDF to FTP site
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest','NegF8LfwK') # open FTP session
    create_ftp_dir_if_does_not_exist(session,'forecast_submissions/'+fc_start_date) # save the forecast directory if it does not exist
    file = open(final_filename,'rb') # read the forecast file
    session.storbinary('STOR forecast_submissions/'+fc_start_date+'/'+final_filename,file) # transfer to FTP site
    file.close() # close the file and quit the session
    session.quit()

#    os.remove(final_filename)

# code to test functions. give it saved netcdf file on PERM
#slp_wk3_predictions = xr.load_dataset('/perm/ecm0847/S2S_comp/'+'slp_20241111_wk3_ECext.nc')
# submit forecasts to FTP site
#AI_WQ_forecast_submission(slp_wk3_predictions,'mslp','20241111','3','ECMWF','EXTrange')


