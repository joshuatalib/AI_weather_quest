Forecast Evaluation
====================================

Forecast Evaluation Modules
----------------------------------------
To aid transparency and replicability throughout the AI Weather Quest, registered participants can evaluate their own submitted predictions after a forecast period has passed. To evaluate forecasts locally, you will need to use the following modules of the `AI_WQ_package`:

- **retrieve_evaluation_data**: Retrieves all the required datasets for local forecast evaluation. 
- **forecast_evaluation**: Includes all the necessary functions to compute area-weighted ranked probability skill scores. 

The following lines of code, import these necessary modules:

.. code-block:: python

  from AI_WQ_package import retrieve_evaluation_data
  from AI_WQ_package import forecast_evaluation

.. important::

  Evaluation at ECMWF will use the same functions and datasets supplied through these modules.

Retrieving Datasets for Forecast Evaluation
---------------------------------------------------

In addition to forecasted probabilities, three datasets are required for forecast evaluation. These datasets, and the important functions within the **retrieve_evaluation_data** module for downloading such data, include:

- Weekly statistics of observed atmospheric characteristics: **retrieve_weekly_obs**.
- Land fraction values which are used to mask out oceanic grid points: **retrieve_land_sea_mask**
- Climatological quintile boundaries which are compared against observed conditions: **retrieve_20yr_quintile_clim**


Weekly observations
^^^^^^^^^^^^^^^^^^^^^^^^
The **retrieve_weekly_obs** function downloads the requested set of observations that are used for forecast evaluation.

.. code-block:: python

  weekly_obs = retrieve_evaluation_data.retrieve_weekly_obs(<<date>>,<<variable>>,<<password>>,<<local_destination>>=None)

- **date** (*str*): The requested date for weekly observations in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

.. note::  
   
   Participants should be able to download relevant observations from mid-January 2024).

.. important::  
   
   The date should correspond to the beginning of the forecast period (i.e. day 19 or day 26) and not the forecast initialisation date (day 1).

- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission portal password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_weekly_obs** function returns a dataset containing the observations that are used for forecast evaluation. For temperature and mean sea level pressure, these observations are based on **ERA5T**, whilst for precipitation, data from the **MSWEP** *NRT* directory is used. Additionally, weekly-means of temperature and pressure are computed using six-hourly data (0, 6, 12 and 18 UTC), whilst for precipitation, weekly-accumulations are computed. The following filename convention is followed for downloaded observations:

.. code-block:: bash

   <<variable>>_obs_<<WEEKLYSTAT>>_<<date>>

where WEEKLYSTAT is either *WEEKLYMEAN* for temperature and pressure, or *WEEKLYSUM* for precipitation. 

Climatological quintile boundaries
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_20yr_quintile_clim* function downloads climatological quintile boundaries.

.. code-block:: python

  clim_quintile_bounds = retrieve_evaluation_data.retrieve_20yr_quintile_boundaries(<<date>>,<<variable>>,<<password>>,local_destination=None)

- **date** (*str*): The requested date for climatological quintile boundaries in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

.. note::  
   
   Participants will only be able to download climatological quintile boundaries associated with a Monday start date.

.. important::  
   
   The date should correspond to the beginning of the forecast period (i.e. day 19 or day 26) and not the forecast initialisation date (day 1).

- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission portal password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_20yr_quintile_boundaries** function returns a dataset containing climatological quintile boundaries. Quintile boundaries have been calculated using the relevant weekly statistic (weekly-mean [tas, mslp]/weekly-sum [pr]) and collating observations from the past twenty years. To expand the sample size to 100 observations, we include data from +/- 4 days at two-day intervals around the requested date. 

.. note:: 

  For temperature and pressure, ERA5 is used for computing quintile climatologies, whilst for precipitation, MSWEP data is utilised. 

Land fraction data
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_land_sea_mask* function downloads land fraction values stored at ECMWF.

.. code-block:: python

  land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(<<password>>,local_destination=None)

- **password** (str): The forecast submission portal password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_land_sea_mask** function returns a dataset containing land fraction values. These values range from 0 to 1, where:

- 0 represents open ocean.
- 1 represents land.
- Intermediate values indicate partial land coverage.

This dataset is used to mask out oceanic grid points when evaluating temperature and precipitation forecasts over land-dominated regions.

.. important::  
   
   Land fraction values are not used when evaluating forecasts of mean sea level pressure. 

Example of retieving all datasets required for evaluation
^^^^^^^^^^^^^^^^^^^^^^^^

Evaluating forecasts using retrieved data
---------------------------------------------------
After downloading the required weekly observations, climatological quintile boundaries and land fraction values, you can now evaluate your forecast. 

The **forecast evaluation** module provides two key functions for computing Ranked Probability Skill Scores (RPSSs):

- **conditional_obs_probs**: Generates an **xarray.dataarray** containing observed probabilities within climatological quintile boundaries. 
- **work_out_RPSS**: Computes the global area-weighted RPSS, benchmarking forecasts against climatology.

Compute observed probabilities
^^^^^^^^^^^^^^^^^^^^^^^^
The *conditional_obs_probs* function determines observed probabilities within a given set of climatological quintile boundaries. The probability is 1 when an observation falls within the specified boundaries.

.. code-block:: python

  obs_pbs = forecast_evaluation.conditional_obs_probs(<<obs>>,<<quintiles>>)

- **obs** (xarray.DataArray): Weekly observations.
- **quintiles** (xarray.DataArray): Climatological quintile boundaries.

Calculate Ranked Probability Skill Score:
^^^^^^^^^^^^^^^^^^^^^^^^
The **work_out_RPSS** function computes the global area-weighted RPSS, measuring forecast accuracy against climatology. 

.. code-block:: python

  RPSS_global_area_weighted = forecast_evaluation.work_out_RPSS(<<fc_pbs>>,<<obs_pbs>>,<<variable>>,<<land_sea_mask>>,quantile_dim='quintile')

- **fc_pbs** (xarray.DataArray): Predicted probabilities between quintile boundaries.
- **obs_pbs** (xarray.DataArray): Observed probabilities (computed using **conditional_obs_probs**).
- **variable** (*str*): The variables being evaluated. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **land_sea_mask** (xarray.DataArray): Dataset containing land fraction values.
- **quantile_dim** (str,default='quintile'): Dimension over which ranked probability scores are aggregated. It is recommended to keep this fixed as 'quintile'.

The **work_out_RPSS** function executes the following tasks:

- Computes the ranked probability score by comparing the cumulative sum of forecast and observed probabilities.
- Calculates the climatological ranked probability score by comparing the cumulative sum of climatological and observed probabilities.
- Determines the RPSS with respect to climatology. 
- Applies a land-sea mask when the examined variable is either temperature or precipitation. Values are set to NaN at grid points with land fraction values less than 80%.
- Computes the area-weighted RPSS.

The final output is the same RPSS displayed on the AI Weather Quest website.

Example evaluating a single forecast
^^^^^^^^^^^^^^^^^^^^^^^^








