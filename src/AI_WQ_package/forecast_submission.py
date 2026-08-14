# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

# python code that will accept quintile, lat, long data and submit forecast to FTP site
import xarray as xr
import numpy as np
import ftplib
import os
import pandas as pd
import io
from datetime import datetime
import subprocess
from sites.sdk.sites import Site, Authenticator
from sites.sdk.sites.utils import FileType
from pathlib import Path
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

def create_ecbox_dir_if_does_not_exist(dir_name,password):
    """
    dir_name: YYYYMMDD, forecast initialisation string
    password: authenication token
    """
    site = Site.from_space_and_name(space='ecbox', name='AI_Weather_Quest')
    # use password to create authenticator
    site_auth = Authenticator.from_token(token=password)
    content_manager = site.get_content_manager(authenticator=site_auth)

    # List only directories
    remote_base = '/forecast_submissions'
    remote_dir = f"{remote_base}/{dir_name}"
    result = content_manager.list(remote_path=remote_base,file_type=FileType.DIR)

    existing_dirs = [f["path"] for f in result["files"]]

    if dir_name in existing_dirs:
        print(f"Directory '{dir_name}' already exists.")
    else:
        print(f"Creating directory '{dir_name}'")
    
        # Create zero-byte placeholder within the chosen directory name.
        placeholder = Path(".keep")
        placeholder.touch()
    
        content_manager.upload(
            local_path=placeholder,
            remote_path=remote_dir,
            upload_zero_byte_files=True
        )
    
        placeholder.unlink()

def AI_WQ_create_empty_dataarray(variable,fc_start_date,fc_period,teamname,modelname,password):
    ''' A function that creates an 'empty' dataarray and supports forecast submission for the AI Weather Quest. 
    The AI WQ advises that users use this function to output an empty dataarray and then fill it with their forecasted values. The function is also used during forecast submission to the FTP site to ensure all participants have the same file structure.
    '''

    # Check filename characteristics and output a string version of fc_period
    fc_period = check_fc_submission.check_filename_characteristics(variable,fc_start_date,fc_period,teamname,modelname)

    if variable != 'MJO' and variable != 'TS': # EDITION 2. Make separate xarrays for MJO and TS.
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
        try: 
            origin_id, expver_id = update_table_unique_identifies(teamname,modelname,password) # EDITION 1
        except:
            origin_id, expver_id = update_table_unique_identifies_ECBOX(teamname,modelname,password)

        # work out forecast issue time
        fc_issue_time = np.datetime64(fc_issue_date+'T00:00:00')
        # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
        da = xr.DataArray(data=empty_data,dims=['quintile','latitude','longitude'],
                coords=dict(quintile=(['quintile'],np.arange(1,6)/5), # outputs [0.2,0.4,0.6,0.8,1.0]
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
    
    elif variable == 'MJO': # EDITION 2, MJO forecasts allowed

        # set standard names of variable
        # need to add cell method - MEAN (tas, mslp) and SUM (pr).
        data_specs = {**{'standard_name':'MJO phase probability','cell_methods':'time: instantaneous (interval: weekly)'},**{'units':'1'}}

        # add shortName
        shortName = 'mjo'
        height = None  # No height for other variables

        fc_issue_date = fc_start_date[:4]+'-'+fc_start_date[4:6]+'-'+fc_start_date[6:]

        # alongside defining the forecast issue date, define the forecasting period in days from forecasting issue date.
        forecast_lags = np.array((7,14,21,28))

        # empty data
        empty_data = np.empty((9,4)) # time, day 7, 14, 21, 28

        # dimension attributes
        MJO_phases = np.arange(9) # Zero = inactive, one to eight = MJO phases
        MJO_attrs = {'units':'MJO phase'}

        # create an appropriate identity names. Unique_ID = origin (characters from teamname [first four + last six - filled with 'z' if needed]). expver_ID (teamname plus '01', '02' etc... where number denotes model number (based on names already in look-up table).
        try:
            origin_id, expver_id = update_table_unique_identifies(teamname,modelname,password) # EDITION 1
        except:
            origin_id, expver_id = update_table_unique_identifies_ECBOX(teamname,modelname,password)

        # work out forecast issue time
        fc_issue_time = np.datetime64(fc_issue_date+'T00:00:00')
        # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
        da = xr.DataArray(data=empty_data,dims=['MJO_phase','valid_time'],
                coords=dict(valid_time=fc_issue_time + forecast_lags.astype('timedelta64[D]'), # outputs time for day 8, 15, 22 and 29
                            MJO_phase=(['MJO_phase'],MJO_phases,MJO_attrs),
                            forecast_issue_date=fc_issue_time,
                            ),
                attrs=dict(**data_specs,description=variable+' prediction from '+teamname+' using '+modelname+' for forecasts at day 7, 14, 21, 28',
                    Conventions='CF-1.6',
                    shortName=shortName,
                    originating_centre=origin_id,
                    expver=expver_id,
                    teamname=teamname,
                    modelname=modelname))
        # add the time attrs
        da.coords['forecast_issue_date'].attrs = {'standard_name': 'forecast_issue_time','long_name': 'forecast issue time','axis':'T'}
    elif variable == 'TS': # Edition 2, tropical storm strike
        # standard for all variables
        # set standard names of variable
        # need to add cell method - MEAN (tas, mslp) and SUM (pr).
        data_specs = {**{'standard_name':'Tropical storm probability','cell_methods':'time: mean (interval: 24 hours)'},**{'units':'1'}}

        # add shortName
        shortName = 'TS'

        height = None  # No height for other variables

        fc_issue_date = fc_start_date[:4]+'-'+fc_start_date[4:6]+'-'+fc_start_date[6:]

        # alongside defining the forecast issue date, define the forecasting period in days from forecasting issue date.
        if fc_period == '1':
            forecast_period_start = 18.0
            forecast_period_end = 24.0
        elif fc_period == '2':
            forecast_period_start = 25.0
            forecast_period_end = 31.0
        forecast_period_bounds = [[forecast_period_start,forecast_period_end]]

        # empty data
        empty_data = np.empty((3,4)) # three terciles, four domains

        # dimension attributes
        basin_attrs = {'long_name':'Oceanic basin'}

        # create an appropriate identity names. Unique_ID = origin (characters from teamname [first four + last six - filled with 'z' if needed]). expver_ID (teamname plus '01', '02' etc... where number denotes model number (based on names already in look-up table).
        try:
            origin_id, expver_id = update_table_unique_identifies(teamname,modelname,password) # EDITION 1
        except:
            origin_id, expver_id = update_table_unique_identifies_ECBOX(teamname,modelname,password)

        # work out forecast issue time
        fc_issue_time = np.datetime64(fc_issue_date+'T00:00:00')
        # With the data, make a dataset array. Streamlining dataset creation so all submissions are the same.
        da = xr.DataArray(data=empty_data,dims=['tercile','basin'],
                coords=dict(tercile=(['tercile'],np.arange(1,4)/3), # outputs [0.33,0.6666,1.0]
                            basin=(['basin'],['ATL','NWP','SWIO','SEIO'],basin_attrs),
                            forecast_issue_date=fc_issue_time,
                            forecast_period_start=fc_issue_time+np.timedelta64(int(forecast_period_start*24), 'h'),
                            forecast_period_end=fc_issue_time+np.timedelta64(int(forecast_period_end*24), 'h'),
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

    return da

def AI_WQ_forecast_submission(data,variable,fc_start_date,fc_period,teamname,modelname,password):
    ''' This function will take a dataset in quintile, lat, long format, save as appropriate netCDF format,
    then copy to FTP site under correct forecast folder, i.e. 20241118. 

    Parameters:
        data (xarray.Dataset): xarray dataset with forecasted probabilites in format (quintile, lat, long). 
        variable (str): Saved variable. Options include 'tas', 'mslp', 'pr', 'TS' and 'MJO'
        fc_start_date (str): The forecast start date as a string in format '%Y%m%d', i.e. 20241118.
        fc_period (str or number): Either forecast period 1 (days 19 to 25) for forecast period 2 (days 26 to 32). # not applicable for MJO
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
    fc_date = datetime.strptime(fc_start_date, "%Y%m%d")
    ftp_closure_date = datetime(2026,8,13)

    if fc_date < ftp_closure_date:  # EDITION 1. USE OF FTP SITE 
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
    else: # EDITION 2, USE OF ecBOX
        # CHECK DIRECTORY EXISTS and if not create it
        create_ecbox_dir_if_does_not_exist(fc_start_date,password)
        # open site
        site = Site.from_space_and_name(space='ecbox', name='AI_Weather_Quest')
        # use password to create authenticator
        site_auth = Authenticator.from_token(token=password)
        # upload content
        content_manager = site.get_content_manager(authenticator=site_auth) 
        remote_path = f"forecast_submissions/{fc_start_date}" # remote path to forecast submission directory for that date
        # UPLOAD file
        content_manager.upload(local_path=f"{final_filename}", remote_path=f"{remote_path}")

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

def update_table_unique_identifies_ECBOX(teamname,modelname,password):
    csv_filename = "AI_WQ_unique_IDs.csv"
   
    # open site
    site = Site.from_space_and_name(space='ecbox', name='AI_Weather_Quest')
    # use password to create authenticator
    site_auth = Authenticator.from_token(token=password)
    # upload content
    content_manager = site.get_content_manager(authenticator=site_auth)

    try:
        # Try reading CSV from ECbox
        csv_content = content_manager.download(remote_path=csv_filename)
        df = pd.read_csv(io.BytesIO(csv_content))
        print(df)
    except Exception as e:
        msg = str(e).lower()

        # file is missing
        if "not found" in msg or "404" in msg:
            print("CSV not found on ECbox — creating new file")

            df = pd.DataFrame(
                columns=["Unique_ID", "expver_ID", "Teamname", "Modelname"]
            )

            with open(csv_filename, "w", encoding="utf-8") as f:
                df.to_csv(f, index=False)

            content_manager.upload(local_path=csv_filename)
            print("New file created and uploaded to ECbox.")

        # file not missing but a different issue
        else:
            raise RuntimeError(
                "AI_WQ_unique_IDs.csv exists but could not be read.\n"
                "This may indicate corruption, permission issues, or a network problem.\n"
                "Refusing to overwrite the file."
            ) from e

    # --------------------------------------------------
    # Update identifiers (same as before)
    # --------------------------------------------------
    df_before = df.copy(deep=True)

    str_identity, str_expver_id, df = generate_identifier(
        teamname, modelname, df
    )
    if not df.equals(df_before):
        with open(csv_filename, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False)
        result = content_manager.upload(local_path=csv_filename)
        print("Updated CSV uploaded to ECbox.")
    else:
        print("No changes - upload to CSV skipped")

    return str_identity, str_expver_id
    
def AI_WQ_check_submission(variable,fc_start_date,fc_period,teamname,modelname,password):
    ''' A function that checks whether a forecast has been successfully submitted to ECMWF. Please note, this function only checks the existence of a forecast and not whether the forecast will conform to the competition rules.
    '''
    # Check filename characteristics and output a string version of fc_period
    fc_period = check_fc_submission.check_filename_characteristics(variable,fc_start_date,fc_period,teamname,modelname)

    # create filename
    final_filename = variable+'_'+fc_start_date+'_p'+fc_period+'_'+teamname+'_'+modelname+'.nc'

    # save new dataset as netCDF to FTP site
    fc_date = datetime.strptime(fc_start_date, "%Y%m%d")
    ftp_closure_date = datetime(2026,8,13)

    if fc_date < ftp_closure_date:  # EDITION 1. USE OF FTP SITE 
        session = ftplib.FTP('ftp.ecmwf.int','ai_weather_quest',password) # open FTP session
        file_exists=False
        try:
            session.cwd(f"/forecast_submissions/{fc_start_date}")
            files = session.nlst() # get list of files
            file_exists = final_filename in files
            if file_exists:
                print (f"File '{final_filename}' exists. You have successfully submitted to the AI Weather Quest")
            else:
                print (f"Could not find '{final_filename}'. Please try resubmitting to the AI Weather Quest.")
        except ftplib.error_perm as e:
            if "550" in str(e):
                print(f"Directory '/forecast_submissions/{fc_start_date}' does not exist. Most likely not a valid forecast initialisation date")
            else:
                raise
    else: # EDITION 2. USE OF ECBOX   
        # open site
        site = Site.from_space_and_name(space='ecbox', name='AI_Weather_Quest')
        # use password to create authenticator
        site_auth = Authenticator.from_token(token=password)
        # upload content
        content_manager = site.get_content_manager(authenticator=site_auth)

        # remote dir that should contain submission
        remote_dir = f"forecast_submissions/{fc_start_date}"

        # get all entries in the remote directory
        try:
            # List directory contents
            entries = content_manager.list(remote_path=remote_dir)
        except Exception as e:
            raise RuntimeError(
                "Authentication or permission error accessing ECbox."
            ) from e
        
        filenames = [os.path.basename(file_entry['path']) for file_entry in entries['files']] # only want filename (no leading directories)
        
        if final_filename in filenames:
            print(f"File '{final_filename}' exists. "
                "You have successfully submitted to the AI Weather Quest.")
        else:
            raise FileNotFoundError(
                 f"Could not find '{final_filename}' after upload. "
                  "Please try resubmitting to the AI Weather Quest.")
