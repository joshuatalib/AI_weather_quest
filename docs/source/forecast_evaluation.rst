Forecast Evaluation
====================================

Forecast Evaluation Modules
----------------------------------------
To aid transparency throughout the AI Weather Quest, registered participants can evaluate their own submitted predictions once a forecast period has passed. To evaluate forecast submissions locally, you will need to use the following modules of the `AI_WQ_package`:

- **retrieve_evaluation_data**: Retrieves all the required datasets to perform forecast evaluation locally. 
- **forecast_evaluation**: Includes all the necessary functions to compute area-weighted RPSSs across land-dominated regions. 

The following lines of code, import these necessary modules for forecast submission:

.. code-block:: python

  from AI_WQ_package import retrieve_evaluation_data
  from AI_WQ_package import forecast_evaluation

.. important::

  Evaluation at ECMWF will use the same functions and datasets supplied through these modules.

Retrieving Datasets for Forecast Evaluation
---------------------------------------------------

Describes datasets required and the necessary functions.

Important functions include:

- **retrieve_weekly_obs**: Downloads weekly statistics of observed atmospheric characteristics ` (see :ref:`Retrieving weekly observations`).
- **retrieve_land_sea_mask**: Downloads land fraction values which are used to mask out oceanic grid points ` (see :ref:`Retrieving climatological quintile boundaries`).
- **retrieve_20yr_quintile_clim**: Downloads climatological quintile boundaries which are compared against observed conditions ` (see :ref:`Retrieving land fraction data`). 


Retrieving weekly observations
^^^^^^^^^^^^^^^^^^^^^^^^
The *retrieve_weekly_obs* function downloads the requested set of observations that are then used for forecast evaluation.

.. code-block:: python

  weekly_obs = retrieve_evaluation_data.retrieve_weekly_obs(<<date>>,<<variable>>,<<password>>)

- **date** (*str*): The requested date for climatological quintile boundaries in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

.. note::  
   
   Participants will only be able to download observations associated with forecast start dates throughout both the training and competitive period of the competition (from June 2025).

- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission portal password provided in your registration email.

The **retrieve_weekly_obs** function returns a dataset containing observations used for forecast evaluation. For temperature and mean sea level pressure these observations are based on ERA5T data, whilst for precipitation, data from the *NRT* directory is used. Additionally, in line with forecast submission requirements, weekly-means of tas and mslp are computed from data at 0, 6, 12 and 18 UTC, whilst for precipitation, weekly-accumulations are computed.  


Retrieving climatological quintile boundaries
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_20yr_quintile_clim* function downloads climatological quintile boundaries that are then used for forecast evaluation.

.. code-block:: python

  clim_quintile_bounds = retrieve_evaluation_data.retrieve_20yr_quintile_boundaries(<<date>>,<<variable>>,<<password>>)

- **date** (*str*): The requested date for climatological quintile boundaries in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

.. note::  
   
   Participants will only be able to download climatological quintile boundaries associated with a Monday start date.

- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (str): The forecast submission portal password provided in your registration email.

The **retrieve_20yr_quintile_boundaries** function returns a dataset containing climatological quintile boundaries. Quintile boundaries have been calculated through using the relevant weekly statistic (weekly-mean [tas, mslp]/weekly-sum [pr]) and then collating observations from the past twenty years. To expand the sample size to 100 observations, we include data from +/- 4 days at two-day intervals around the requested date. 

.. note:: 

  For temperature and pressure, ERA5 is used for computing quintile climatologies, whilst for precipitation, MSWEP data is utilised. 

Retrieving land fraction data
^^^^^^^^^^^^^^^^^^^^^^^^

The *retrieve_land_sea_mask* function within the *retrieve_evaluation_data* module will call land fraction values stored at ECMWF and used for evaluation.

.. code-block:: python

  land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(<<password>>)

- **password** (str): The forecast submission portal password provided in your registration email.

The **retrieve_land_sea_mask** function returns a dataset containing land fraction values. These values range from 0 to 1, where:

- 0 represents open ocean.
- 1 represents land.
- Intermediate values indicate partial land coverage.

This dataset is used to mask out oceanic grid points when evaluating forecasts over land-dominated regions.

Example of retieving all datasets required for evaluation
^^^^^^^^^^^^^^^^^^^^^^^^

Evaluating forecasts using retrieved data
---------------------------------------------------




