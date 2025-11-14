Forecast Evaluation
====================================

Importing Forecast Evaluation Modules
----------------------------------------
To ensure transparency and replicability throughout the AI Weather Quest, registered participants can evaluate their own submitted forecasts after a forecast window has passed. The **AI-WQ-Package** provides dedicated modules for local forecast evaluation:

- **retrieve_evaluation_data**: Downloads all the necessary datasets for local forecast evaluation. 
- **forecast_evaluation**: Contains functions to compute area-weighted Ranked Probability Skill Scores (RPSSs). 

To import these modules, use the following:

.. code-block:: python

  from AI_WQ_package import retrieve_evaluation_data
  from AI_WQ_package import forecast_evaluation

.. important::

  Evaluation at ECMWF will use the same functions and datasets supplied through these modules.

Retrieving Datasets for Forecast Evaluation
---------------------------------------------------

In addition to forecasted probabilities, three datasets are required for forecast evaluation. These datasets, and the important functions within the **retrieve_evaluation_data** module for downloading such data, include:

- Weekly statistics of observed atmospheric characteristics: **retrieve_weekly_obs**.
- Climatological quintile boundaries which are compared against observed conditions: **retrieve_20yr_quintile_clim**
- Land fraction values which are used to exclude oceanic grid points: **retrieve_land_sea_mask**

.. important::  
   
   When downloading historical atmospheric characteristics, the date should correspond to the beginning of the forecast window (i.e. day 19 or day 26) and not the forecast initialisation date (day 1). Additionally, participants will only be able to download weekly observations commencing on a Monday.

Weekly observations
^^^^^^^^^^^^^^^^^^^^^^^^
The **retrieve_weekly_obs** function downloads the requested set of observations that are used for forecast evaluation.

.. code-block:: python

  weekly_obs = retrieve_evaluation_data.retrieve_weekly_obs(<<date>>,<<variable>>,<<password>>,<<local_destination>>=None)

- **date** (*str*): The requested date for weekly observations in format `YYYYMMDD` (e.g., `'20250519'` for 19th May 2025).

.. note::  
   
   Participants should be able to download relevant observations from mid-January 2024.

- **variable** (*str*): The requested atmospheric variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_weekly_obs** function returns the dataset used for forecast evaluation. All variables are derived using **ERA5T** data. Weekly-mean temperature and pressure are calculated from six-hourly data (00, 06, 12, and 18 UTC), whilst hourly data is used for precipitation.

**Filename Convention**

Downloaded observations follow this naming pattern:

.. code-block:: bash

   <<variable>>_obs_<<weekly_statistic>>_<<date>>

where **weekly_statistic** is either 'WEEKLYMEAN' (for temperature and pressure) or 'WEEKLYSUM' (for precipitation). 

Climatological quintile boundaries
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_20yr_quintile_clim* function downloads climatological quintile boundaries.

.. code-block:: python

  clim_quintile_bounds = retrieve_evaluation_data.retrieve_20yr_quintile_clim(<<date>>,<<variable>>,<<password>>,local_destination=None)

- **date** (*str*): The requested date for climatological quintile boundaries in format `YYYYMMDD` (e.g., `'20250519'` for 19th May 2025).
- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_20yr_quintile_clim** function returns a dataset containing climatological quintile boundaries. Quintile boundaries have been calculated using the relevant weekly statistic (weekly-mean [tas, mslp]/weekly-sum [pr]) and collating observations from the past twenty years. To expand the sample size to 100 observations, we include data from +/- 4 days at two-day intervals around the requested date (i.e. Thursday (day -4), Saturday (day -2), Monday (day 0), Wednesday (day 2), Friday (day 4)). 

.. important::  
   
   Climatological quintile boundaries are available at a daily resolution from 11th January 1999 to present day plus eight months. 

Land fraction data
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_land_sea_mask* function retrieves land fraction values from ECMWF.

.. code-block:: python

  land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(<<password>>,local_destination=None)

- **password** (*str*): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_land_sea_mask** function returns a dataset containing land fraction values. These values range from 0 to 1, where:

- 0 represents open ocean.
- 1 represents land.
- Intermediate values indicate partial land coverage.

This dataset is used to mask oceanic grid points when evaluating temperature and precipitation forecasts.

.. important::  
   
   Land fraction values are not used when evaluating forecasts of mean sea level pressure. 

Example: Retrieving Required Datasets
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AI_WQ_package import retrieve_evaluation_data

   # Download weekly observations
   obs = retrieve_evaluation_data.retrieve_weekly_obs('20250519','tas',<<password>>)
   # Download historical quintile boundaries 
   quintile_clim = retrieve_evaluation_data.retrieve_20yr_quintile_clim('20250519','tas',<<password>>)
    
   # Download land-sea mask
   land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(<<password>>)

This example retrieves all necessary datasets for evaluating near-surface temperature forecasts for the week starting May 19th 2025.

Evaluating Forecasts Using Retrieved Data
---------------------------------------------------
After downloading the required weekly observations, climatological quintile boundaries and land fraction values, you can now evaluate your forecast. 

The **forecast evaluation** module provides two key functions for computing Ranked Probability Skill Scores (RPSSs):

- **conditional_obs_probs**: Generates an **xarray.dataarray** containing observed probabilities within climatological quintile boundaries. 
- **work_out_RPSS**: Computes the global area-weighted ranked probability skill score, benchmarking forecasts against climatology.

Compute observed probabilities
^^^^^^^^^^^^^^^^^^^^^^^^
The *conditional_obs_probs* function determines observed probabilities within a given set of climatological quintile boundaries. The probability is 1 when an observation falls within the specified boundaries.

.. code-block:: python

  obs_pbs = forecast_evaluation.conditional_obs_probs(<<obs>>,<<quintile_bounds>>)

- **obs** (*xarray.DataArray*): Weekly observations.
- **quintile_bounds** (*xarray.DataArray*): Climatological quintile boundaries.

Calculate Ranked Probability Skill Score
^^^^^^^^^^^^^^^^^^^^^^^^
The **work_out_RPSS** function computes the global area-weighted RPSS, measuring forecast accuracy against climatology. 

.. code-block:: python

  RPSS_global_area_weighted = forecast_evaluation.work_out_RPSS(<<fc_pbs>>,<<obs_pbs>>,<<variable>>,<<land_sea_mask>>,quantile_dim='quintile')

- **fc_pbs** (*xarray.DataArray*): Predicted probabilities between quintile boundaries.
- **obs_pbs** (*xarray.DataArray*): Observed probabilities (computed using **conditional_obs_probs**).
- **variable** (*str*): The variables being evaluated. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **land_sea_mask** (*xarray.DataArray*): Dataset containing land fraction values.
- **quantile_dim** (*str, default='quintile'*): Dimension over which ranked probability scores are aggregated. It is recommended to keep this fixed as 'quintile'.

The **work_out_RPSS** function executes the following tasks:

- Computes a ranked probability score by comparing the cumulative sum of forecast and observed probabilities.
- Calculates the climatological ranked probability score by comparing the cumulative sum of climatological and observed probabilities.
- Determines the RPSS with respect to climatology. 
- Applies a land-sea mask when the variable is either temperature or precipitation. Values are set to NaN at grid points with land fraction values less than 50%.
- Computes the area-weighted RPSS.

.. important::  
   
   Land fraction values are not used when evaluating forecasts of mean sea level pressure. 

The final output is the same RPSS displayed on the AI Weather Quest website.

Example evaluating a single forecast
^^^^^^^^^^^^^^^^^^^^^^^^

Continuing from the example above, the following code illustrates the evaluation of temperature forecasts for the week commencing 19th May 2025. 

.. code-block:: python

   from AI_WQ_package import forecast_evaluation

   # compute observed probabilities
   obs_pbs = forecast_evaluation.conditional_obs_probs(obs,quintile_clim)

   # compute global RPSS
   global_RPSS = forecast_evaluation.work_out_RPSS(submitted_forecast,obs_pbs,'tas',land_sea_mask)

Example computing period-aggregated scores
^^^^^^^^^^^^^^^^^^^^^^^^

Participants can compute period-aggregated scores by aggregating forecasts over multiple initialization dates within a competitive period. This requires retrieving a list of forecast initialization dates.

The function **retrieve_all_period_fcdates** retrieves all initialisation dates within the same competitive period up to a given forecast initialisation date: 

.. code-block:: python

  all_fc_dates = retrieve_evaluation_data.retrieve_all_period_fcdates(<<fc_init_date>>,<<password>>)

- **fc_init_date** (*str*): The latest forecast initialisation date in the format *YYYYMMDD* (e.g., ‘20250519’ for 19th May 2025). 
- **password** (*str*): The forecast submission password provided in your registration email.

Once the forecast initialization dates are retrieved, the period-aggregated score is computed by iterating through each date:

.. code-block:: python

   from AI_WQ_package import forecast_evaluation, retrieve_evaluation_data
   import numpy as np
   import xarray as xr
   from datetime import datetime, timedelta

   # user defined parameters
   fc_init_date = '20250717' # example of 17th July 2025
   variable = 'tas' # example of near-surface air temperature
   lead_time = '1' # The selected forecasting window ('1': days 19 to 25, '2': days 26 to 32)
   password = 'registration_password' # replace with the registration password recieved in your welcome email.

   # retrieve forecast initialisation dates within the competitive period

   all_fc_dates = retrieve_evaluation_data.retrieve_all_period_fcdates(fc_init_date,password)

   # initialise arrays to store ranked probability scores (RPSs)
   all_fc_RPS = []
   all_clim_RPS = []

   # retrieve land-sea mask
   land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(password)

   for fc_init in all_fc_dates: # loop through all the forecast dates within the competitive period
       # TO DO: USER MUST RETRIEVE ACTUAL FORECAST DATA! Would recommend opening the submitted forecast as a xr.dataarray
       submitted_forecast = submitted_forecast

       # retrieve observations for the appropriate week
       # work out forecast start date (i.e. Monday start - based on lead_time).
       date_obj = datetime.strptime(fc_init,"%Y%m%d") # get initial date as a date obj 

       # add number of days to date object depending on lead time
       if lead_time == '1':
           fc_valid_date_obj = date_obj + timedelta(days=4+(7*2)) # get to the next Monday then add number of weeks
       elif lead_time == '2':
           fc_valid_date_obj = date_obj + timedelta(days=4+(7*3))

       fc_valid_date = fc_valid_date_obj.strftime("%Y%m%d") # convert date obj back to a string

       # Download observations
       obs = retrieve_evaluation_data.retrieve_weekly_obs(fc_valid_date,variable,password)
       # Download climatology
       quintile_clim = retrieve_evaluation_data.retrieve_20yr_quintile_clim(fc_valid_date,variable,password)

       # work out which quintile bound the observation sits in
       obs_pbs = forecast_evaluation.conditional_obs_probs(obs,quintile_clim)

       # work out RPSs
       RPS_fc = forecast_evaluation.calculate_RPS(submitted_forecast,obs_pbs,variable,land_sea_mask,lat_weighting=True,global_mean=False) # work out RPS for forecast but keep full 2D grid with weights included.
       # work out RPS_clim. # create a climatological xarray with all values equal to 0.2
       num_quants = submitted_forecast.shape[0]
       clim_pbs = obs_pbs.where(False,1.0/num_quants)
       RPS_clim = forecast_evaluation.calculate_RPS(clim_pbs,obs_pbs,variable,land_sea_mask,lat_weighting=True,global_mean=False)

       all_fc_RPS.append(RPS_fc) # for each initialisation date, append the two arrays
       all_clim_RPS.append(RPS_clim)
   # once all the RPSs have been calculated, compute final RPSS.
   all_fc_RPS_combined_avg = xr.concat(all_fc_RPS,dim="forecast_period_start").mean() # take an average across forecast initialisation date after concatenating all forecasts together. Averages temporally and spatially at the same time.

   all_clim_RPS_combined_avg = xr.concat(all_clim_RPS,dim="forecast_period_start").mean()

   # work out single RPSS score. This score is the computed period-aggregated score.  
   single_RPSS_score = 1-(all_fc_RPS_combined_avg.values/all_clim_RPS_combined_avg.values)
