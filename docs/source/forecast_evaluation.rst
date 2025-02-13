Forecast Evaluation
====================================

Forecast Evaluation Modules
----------------------------------------
To aid transparency and replicability throughout the AI Weather Quest, registered participants can evaluate their own submitted predictions after a forecast period has passed (day 37). To evaluate forecasts locally, you will need to use the following modules of the `AI_WQ_package`:

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
The *retrieve_weekly_obs* function downloads the requested set of observations that are used for forecast evaluation.

.. code-block:: python

  weekly_obs = retrieve_evaluation_data.retrieve_weekly_obs(<<date>>,<<variable>>,<<password>>,<<local_destination>>=None)

- **date** (*str*): The requested date for weekly observations in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

.. note::  
   
   Participants will only be able to download observations associated with forecasts within the training and competitive periods of the competition (i.e. from June 2025).

.. important::  
   
   The date should correspond to the beginning of the forecast period (i.e. day 19 or day 26) and not the forecast initialisation date (day 1).

- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission portal password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

The **retrieve_weekly_obs** function returns a dataset containing the observations that are used for forecast evaluation. For temperature and mean sea level pressure, these observations are based on ERA5T, whilst for precipitation, data from the *NRT* directory is used. Additionally, in line with forecast submission requirements, weekly-means of tas and mslp are computed from data at 0, 6, 12 and 18 UTC, whilst for precipitation, weekly-accumulations are computed.  


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




