# python code that will accept quintile, lat, long data and submit forecast to FTP site
import xarray as xr
import numpy as np
import ftplib
import os
import pandas as pd
import io
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

def AI_WQ_create_empty_dataarray(variable,fc_start_date,fc_period,teamname,modelname,password):
    ''' A function that creates an 'empty' dataarray and supports forecast submission for the AI Weather Quest. 
    The AI WQ advises that users use this function to output an empty dataarray and then fill it with their forecasted values. The function is also used during forecast submission to the FTP site to ensure all participants have the same file structure.
    '''

    # Check filename characteristics and output a string version of fc_period
    fc_period = check_fc_submission.check_filename_characteristics(variable,fc_start_date,fc_period,teamname,modelname)

    # standard for all variables
    standard_names_all_vars = {'units':'1','coordinates':'latitude longitude'}

    # set standard names of variable
    # need to add cell method - MEAN (tas, mslp) and SUM (pr).
    if variable == 'mslp':
        data_specs = {**{'standard_name':'Mean sea level pressure probability','cell_methods':'time: mean (interval: 6 hours)'},**standard_names_all_vars}
    elif variable == 'tas':
        data_specs = {**{'standard_name':'2 metre temperature probability','cell_methods':'time: mean (interval: 6 hours)'},**standard_names_all_vars}
    elif variable == 'pr':
        data_specs = {**{'standard_name':'Total precipitation probability','cell_methods':'time: sum (interval: 24 hours)'},**standard_names_all_vars}

    # add shortName
    if variable == 'pr':
        shortName = 'tp'
    elif variable == 'tas':
        shortName = 't2m'
    elif variable == 'mslp':
        shortName = 'mslp'

    # add a height dimension if tas
    if variable == 'tas':
        height = 2  # Assuming height is at near-surface level (2 m), modify if needed
        height_attrs = {
        'standard_name': 'height',
        'units': 'm',
        'positive': 'up',
        'axis': 'Z'
                        }
    else:
        height = None  # No height for other variables

    fc_issue_date = fc_start_date[:4]+'-'+fc_start_date[4:6]+'-'+fc_start_date[6:]

    # alongside defining the forecast issue date, define the forecasting period in days from forecasting issue date.
    if fc_period == '1':
        forecast_period_start = 18.0
        if variable == 'mslp' or variable == 'tas':
            forecast_period_end = 24.75
        elif variable == 'pr':
            forecast_period_end = 25.0
    elif fc_period == '2':
        forecast_period_start = 25.0
        if variable == 'mslp' or variable == 'tas':
            forecast_period_end = 31.75
        elif variable == 'pr':
            forecast_period_end = 32.0
    forecast_period_bounds = [[forecast_period_start,forecast_period_end]]

    # empty data
    empty_data = np.empty((5,121,240))

    # dimension attributes
    lat_attrs = {'units':'degrees_north','long_name':'latitude','standard_name':'latitude','axis':'X'}
    lon_attrs = {'units':'degrees_east','long_name':'longitude','standard_name':'longitude','axis':'Y'}
    latitude = np.arange(90.0,-91.0,-1.5) # based on 1.5 deg grid
    longitude = np.arange(0.0,360.0,1.5)

    # create an appropriate identity names. Unique_ID = origin (characters from teamname [first four + last six - filled with 'z' if needed]). expver_ID (teamname plus '01', '02' etc... where number denotes model number (based on names already in look-up table).
    origin_id, expver_id = update_table_unique_identifies(teamname,modelname,password)

    # work out forecast issue time
    fc_issue_time = np.datetime64(fc_issue_date+'T00:00:00')
    # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
    da = xr.DataArray(data=empty_data,dims=['quintile','latitude','longitude'],
            coords=dict(quintile=(['quintile'],np.arange(0.2,1.1,0.2)), # outputs [0.2,0.4,0.6,0.8,1.0]
                        latitude=(['latitude'],latitude,lat_attrs),
                        longitude=(['longitude'],longitude,lon_attrs),
                        forecast_issue_date=fc_issue_time,
                        forecast_period_start=fc_issue_time+np.timedelta64(int(forecast_period_start*24), 'h'),
                        forecast_period_end=fc_issue_time+np.timedelta64(int(forecast_period_end*24), 'h'),
                        height=height if height is not None else None
                        ),
            attrs=dict(**data_specs,description=variable+' prediction from '+teamname+' using '+modelname+' for forecasting period '+str(fc_period),
                Conventions='CF-1.6',
                forecast_period_bounds_units='days into forecast',
                forecast_period_bounds=f"[{forecast_period_start},{forecast_period_end}]",
                shortName=shortName,
                originating_centre=origin_id,
                expver=expver_id,
                teamname=teamname,
                modelname=modelname))
    # add the time attrs
    da.coords['forecast_issue_date'].attrs = {'standard_name': 'forecast_issue_time','long_name': 'forecast issue time','axis':'T'}
    da.coords['forecast_period_start'].attrs = {'long_name': 'forecast period start','axis':'T'} 
    da.coords['forecast_period_end'].attrs = {'long_name': 'forecast period end','axis':'T'}

    if height is not None:
        da.coords['height'].attrs = height_attrs

    return da

def AI_WQ_forecast_submission(data,variable,fc_start_date,fc_period,teamname,modelname,password):
    ''' This function will take a dataset in quintile, lat, long format, save as appropriate netCDF format,
    then copy to FTP site under correct forecast folder, i.e. 20241118. 

    Parameters:
        data (xarray.Dataset): xarray dataset with forecasted probabilites in format (quintile, lat, long). 
        variable (str): Saved variable. Options include 'tas', 'mslp' and 'pr'.
        fc_start_date (str): The forecast start date as a string in format '%Y%m%d', i.e. 20241118.
        fc_period (str or number): Either forecast period 1 (days 19 to 25) for forecast period 2 (days 26 to 32).
        teamname (str): The teamname that was submitted during registration.
        modelname (str): Modelname for particular forecast. Teams are only allowed to submit three models each.

    '''
    ###############################################################################################################
    # CHECKING DATA FORMAT AND INPUTTED VARIABLES
    # outputs the data (dataarray) and final filename
    data, final_filename = check_fc_submission.all_checks(data,variable,fc_start_date,fc_period,teamname,modelname)

    data_only = data.values # this should be shaped, quintile, latitude, longitude. check has been made in all_checks

    submitted_da = AI_WQ_create_empty_dataarray(variable,fc_start_date,fc_period,teamname,modelname,password) # create an empty dataarray.
    submitted_da.values = data_only

    submitted_da.to_netcdf(final_filename) # save netcdf file temporaily where the script is being run
    
    ################################################################################################################
    
    # save new dataset as netCDF to FTP site
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password) # open FTP session
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

def generate_identifier(teamname, modelname,df):
    # Normalize teamname to ensure it has 4+2 characters
    first_four = teamname[:4]  # First 4 characters
    last_two = teamname[-2:]   # Last 2 characters
    normalized_teamname = first_four + last_two  # Combine them
    
    # Pad with 'z' if necessary
    if len(teamname) < 4:
        normalized_teamname = (teamname + "zz")[:6]
    elif len(teamname) < 6:
        normalized_teamname = (teamname[:4] + 'z' * (6 - len(teamname)))[0:6]

    # Check if the model already exists
    existing_entry = df[(df["Teamname"] == teamname) & (df["Modelname"] == modelname)]
    if not existing_entry.empty:
        return existing_entry["Unique_ID"].values[0], existing_entry["expver_ID"].values[0], df

    # Count existing models for this team
    team_models_count = df[df["Teamname"] == teamname].shape[0] + 1

    # Generate new identifier
    new_identifier = f"{normalized_teamname}_{team_models_count:02d}"
    expver_identifier = f"{teamname}_{team_models_count:02d}"

    # Append new entry to DataFrame
    expected_columns = ["Unique_ID", "expver_ID", "Teamname", "Modelname"]

    new_row = pd.DataFrame({
        "Unique_ID": [new_identifier],
        "expver_ID": [expver_identifier],
        "Teamname": [teamname],
        "Modelname": [modelname]
        }, columns=expected_columns)

    df = pd.concat([df, new_row],axis=0,ignore_index=True,sort=False)

    return new_identifier, expver_identifier, df

def update_table_unique_identifies(teamname,modelname,password):
    csv_filename = "AI_WQ_unique_IDs.csv"
    # read in .csv file stored on ftp site - table of identifies that is stored on FTP site.
    session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password)
    try:
        csv_data = io.StringIO()
        session.retrlines(f"RETR {csv_filename}", lambda line: csv_data.write(line + "\n"))
        csv_data.seek(0)
        df = pd.read_csv(csv_data)
        print (df)
    except Exception as e:
        # if file does not exist, create one and upload to FTP site.
        print (f"File not found on FTP. Creating a new file. Error: {e}")

        # Define an empty DataFrame with the expected structure
        df = pd.DataFrame(columns=["Unique_ID", "expver_ID", "Teamname", "Modelname"])

        # Upload the empty file to initialize it on the FTP server
        csv_output = io.StringIO()
        df.to_csv(csv_output, index=False)  # Ensure we don't include an index column
        csv_output.seek(0)
        session.storbinary(f"STOR {csv_filename}", io.BytesIO(csv_output.getvalue().encode()))
        print("New file created and uploaded to FTP.") 

    # a function that generates a unique identifier if one cannot be found associated with the model or teamname.
    str_identity, str_expver_id, df = generate_identifier(teamname,modelname,df)    
 
    csv_output = io.StringIO()
    df.to_csv(csv_output,index=False)
    csv_output.seek(0)

    session.storbinary(f"STOR {csv_filename}", io.BytesIO(csv_output.getvalue().encode()))
    session.quit()

    return str_identity, str_expver_id

