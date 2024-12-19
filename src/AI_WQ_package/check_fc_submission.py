# script to check netCDF file for forecast submission
import xarray as xr
import numpy as np
import ftplib
from datetime import datetime, timedelta

def check_variable_in_list(variable_name, expected_values):
    if variable_name not in expected_values:
        raise ValueError(f"Expected one of {expected_values}, but got {variable_name}.")

def check_forecast_data_window(fc_start_date):
    # use datetime to convert string into date_obj
    date_obj = datetime.strptime(fc_start_date,'%Y%m%d')
    # date_obj should be a Thursday! In alignment with dynamical models.
    if date_obj.weekday() != 3:
        raise ValueError(f"Forecast start date of {fc_start_date} is not a Thursday. All forecast start dates should be a Thursday to enable a direct comparison between AI/ML models and dynamical models.")

    # check that it is within allotted time window
    # Start of Thursday to end of Sunday
    now = datetime.utcnow()

    # get succeeding Sunday (the date should be a Thursday so add 3 days
    next_sunday = date_obj+timedelta(days=3)
    # set time to 23:59:59
    end_of_next_sun = next_sunday.replace(hour=23,minute=59,second=59,microsecond=59)
    end_of_next_sun_str = end_of_next_sun.strftime('%Y%m%d')

    # check chosen data is within the Wednesday to Tuesday alloted timewindow
    if date_obj <= now <= end_of_next_sun:
        print ('forecast submitted within competition time window')
    else:
        raise ValueError(f"You are not allowed to submit a forecast for the following forecast start date, {fc_start_date}, at this point in time. Allowed time window for this forecast start date is {fc_start_date} to {end_of_next_sun_str}")

def convert_fc_period_to_string(value):
    # convert the fc_period to a string for saving
    if isinstance(value,(int,float)):
        return str(int(value)) # save a string of the integer value
    elif isinstance(value,(str)):
        return value # if it already is a string, just return the string value
    else:
        raise ValueError(f"The value '{value}' is not a number nor str.")

def check_and_flip_latitudes(da):
    """
    Check if latitudes range from 90 to -90, and flip if necessary.

    Parameters:
        da (xarray.DataArray): The dataarray to check.

    Returns:
        xarray.DataArray: The modified dataarray with corrected latitude ordering. Latitude ordering should always be 90 to -90.
    """
    # Check if the latitude variable exists
    # find latitude name
    latitude_names = ['latitude', 'lat', 'latitudes', 'lat_deg', 'y']
    latitude = None
    for name in latitude_names:
        if name in da.coords:
            latitude = da[name] # extract the coordinate
            latitude_vals = da[name].values # extract latitude values
            print(f"Latitude found as '{name}'")
            break

    if latitude is None:
        raise ValueError(f"Latitude coordinate not found in the dataset. Tried '{latitude_names}.'")

    if latitude_vals.shape[0] != 181:
        raise ValueError(f"Latitude coordinate does not have 181 points. Require 181 points (90 to -90 at resolution of 1 deg) to submit'")

    # Check if latitudes need to be flipped
    if latitude_vals[0] < latitude_vals[-1]:  # If increasing order
        print("Latitudes are in ascending order (first latitude point is bigger than last latitude point); flipping them to descend from 90 to -90.")
        da = da.sortby(latitude, ascending=False)
    return da

def check_quintile_range(da):
    ''' function that checks that quintiles within the dataarray are labelled 0.2, 0.4, 0.6, 0.8 and 1.0

    Parameters:
        da (xarray.DataArray): The DataArray to check.

    Returns:
        If the DataArray does not have quintile values equal to 0.2, 0.4, 0.6, 0.8 and 1.0, raises a value error.
    '''
    expected_quintiles = {0.2,0.4,0.6,0.8,1.0}

    # looping through possible quintile names
    q_names = ['quintile', 'Quintile', 'q', 'percentile', 'Q']
    quintile = None
    for name in q_names:
        if name in da.coords:
            quintile = da[name] # extract the coordinate
            quintile_vals = da[name].values # extract latitude values
            print(f"Quintile found as '{name}'")
            break

    if quintile is None:
        raise ValueError(f"Quintile coordinate not found in the dataset. Tried '{q_names}.'")

    # check quintile values are similar (tolarance of 1e-8)
    if not np.allclose(sorted(list(expected_quintiles)), sorted(quintile_vals)):
        raise ValueError(f"'{name}' coordinate values do not match the expected values. Found: {quintile_vals}, expected: {expected_quintiles}.")

    return da

def check_and_convert_longitudes(ds):
    """
    Check if longitudes range from 0 to 360 and convert if necessary.

    Parameters:
        ds (xarray.Dataset): The dataset to check.

    Returns:
        xarray.Dataset: The modified dataset with longitudes converted to 0 to 360 range.
    """
    # Check if the longitude name exists
    # find longitude name
    longitude_names = ['longitude', 'lon', 'longitudes', 'lon_deg', 'x']
    longitude = None
    for name in longitude_names:
        if name in ds.coords:
            longitude = ds[name] # extract the coordinate
            longitude_vals = ds[name].values # extract the values
            print(f"Longitude found as '{name}'")
            break

    if longitude is None:
        raise ValueError(f"Longitude coordinate not found in the dataset. Tried '{longitude_names}.'")

    if longitude_vals.shape[0] != 360:
        raise ValueError(f"Longitude coordinate does not have 360 points. Require 360 points (0 to 359 (inclusive) at resolution of 1 deg) to submit'")

    # Check if longitudes are in the -180 to 180 range
    if np.any(longitude_vals < 0):
        print("Assuming longitudes are in the -180 to 180 range; converting to 0 to 360.")
        longitudes = (longitudes + 360) % 360  # Convert to 0 to 360 range
        ds = ds.assign_coords({name: longitudes})  # Update the dataset's longitude coordinates with 0 to 360. 
    return ds

def check_data_characteristics(da):
    # check all data is between 0.0 and 1.0
    all_within_range = True
    
    if not ((da.values >= 0) & (da.values <= 1) | np.isnan(da.values)).all():
        all_within_range = False

    if all_within_range:
        print("All data is between 0 and 1.")
    else:
        raise ValueError(f"Submitted dataarray has values outside the range of 0 and 1. Nans are also permitted.")

    # check data shape is (5,181,360)
    expected_shape = (5, 181, 360)
    if da.shape != expected_shape:
        raise ValueError(f"DataArray shape is {da.shape}, but expected {expected_shape}.")

    # check all probabilities equal 1.0 when summing across axis.
    summed_values = da.sum(axis=0)
    if not np.allclose(summed_values,1.0,atol=1e-3):
        raise ValueError("Values do not sum to 1.0 along the first axis.")

def is_valid_date(input_str):
    try:
        # Attempt to parse the input string with the desired format
        datetime.strptime(input_str, '%Y%m%d')
    except ValueError:
        raise ValueError(f"'{input_str}' is NOT a valid date in the format '%Y%m%d'. Please check.")

def check_filename_characteristics(variable,fc_start_date,s2s_time_period,teamname,modelname):
    # (1) first check submitted variables except for the dataset, i.e. components of the filename.
    # (1.a) check submitted variable name. - only allowed to submit 'tas', 'mslp' and 'pr'
    check_variable_in_list(variable,['tas','mslp','pr'])

    # (1.b) check the fc_start_date is appropriate format
    is_valid_date(fc_start_date)

    # (1.c) convert forecast period to a string and check it is 1 or 2.
    s2s_time_period = convert_fc_period_to_string(s2s_time_period)
    check_variable_in_list(s2s_time_period,['1','2'])

    # (1.d) TO ADD: CHECK THE TEAMNAME AND MODELNAME HAVE BEEN REGISTERED!


    return s2s_time_period


def all_checks(data,variable,fc_start_date,s2s_time_period,teamname,modelname):
    ''' This function performs all checks on submitted fields.
    Parameters:
        data (xarray.DataArray): xarray DataArray with forecasted probabilites in format (quintile, lat, long).
        variable (str): Saved variable. Options include 'tas', 'mslp' and 'pr'.
        fc_start_date (str): The forecast start date as a string in format '%Y%m%d', i.e. 20241118.
        s2s_time_period (str or number): The two periods that we are requesting forecasts (Days 18–24 and Days 25–31) will be submitted as '1' or 1, i.e. '1' or 1. # the two values allowed, 1 or 2, to denote the two periods requested
        teamname (str): The teamname that was submitted during registration.
        modelname (str): Modelname for particular forecast. Teams are only allowed to submit three models each.

    '''
    # (1) first check all components of filename. OUTPUTS S2S time period as a string.
    s2s_time_period = check_filename_characteristics(variable,fc_start_date,s2s_time_period,teamname,modelname)
    
    # after checking all components of the filename, create a final filename that will be used to save the file!
    final_filename = variable+'_'+fc_start_date+'_p'+s2s_time_period+'_'+teamname+'_'+modelname+'.nc'

    # (2) Check the submitted xarray dataset.
    # (2.a) check forecast date is within appropriate range
#    check_forecast_data_window(fc_start_date)

    # (2.b) check spatial components. - the components also check the domain size and the spacing between them (should be 1.0) for each.
    # (2.bi) lat range [should be 90, -90 , 'degrees_north']
    data = check_and_flip_latitudes(data)
    # (2.bii) long range [should be 0 to 359.0,'degrees_east']
    data = check_and_convert_longitudes(data)

    # (2.c) check the quintile range 
    data = check_quintile_range(data)    

    # (2.d) check data characteristics
        # checks all data is between 0 and 1.0
        # checks data shape is equal to (5, 181, 360)
        # checks probabilities equal 1.0 when summing across first axis (quintile)
    check_data_characteristics(data)


    return data, final_filename





