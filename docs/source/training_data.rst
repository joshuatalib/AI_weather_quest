Training Data
======================================

Participants can use any observational, forecast or reanalysis dataset to develop their AI/ML sub-seasonal forecasting models. To facilitate initial model development, registered participants can download post-processed ERA5 and MSWEP data from ECMWF. 

Accessing Available Data
--------------------------------------
The following datasets at a 1.5 degree resolution have been made easily accessible:

- `ERA5 <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview>`_ data (1979 - 2024):
   - Weekly-mean temperature (K)
   - Weekly-mean mean sea level pressure (Pa)
- `MSWEP <https://www.gloh2o.org/mswep/>`_ data (1979 - 2024):
   - Weekly-accumulated precipitation (mm week\ :sup:`-1`)

.. important::  
   
   At the launch of the AI Weather Quest, post-processed training data is available from the 2nd January 1979 to 30th November 2024. Code for automatically updating available training data is currently in development.

Importing the Retrieve Training Data Module
--------------------------------------------
To download post-processed ERA5 or MSWEP data, you will need functions from the `retrieve_training_data.py` module. The key function within this module is:

- **retrieve_annual_training_data**: Download annual files containing weekly statistics for temperature (tas), mean sea level pressure (mslp) or precipitation (pr).

To import the necessary module, use the following Python code:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

Downloading Training Data
--------------------------------------------

Historical data, stored in annual files, can be retrieved using the `retrieve_annual_training_data` function:

.. code-block:: python

   retrieve_annual_training_data(<<year>>,<<variable>>,<<password>>,<<local_destination>>=None)

- **year** (*int*): The year of requested data, i.e. 2000. The year must be between 1979 and 2024 inclusive. 
- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (*str*): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

.. note::  
   
   The function only supports the variables listed above. Additionally, each file is approximately 41 MB and contains weekly statistics at a daily, 1.5 degree resolution. Participants should ensure they have adequate storage space if downloading multiple years.

Understanding Data Processing Details
--------------------------------------------
ERA5 Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Downloaded at six-hourly intervals (0, 6, 12 and 18 UTC) at a 1.5 degree resolution.
- Seven-day rolling means are computed, with time axis labels indicating the start of each 7-day period. 

MSWEP Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Data before 2021 was sourced from the *Past* directory, whilst data from 2021 onwards is from the *NRT* directory. 
- Daily rainfall accumulations are regridded to a 1.5-degree resolution using first-order conservative remapping (`CDO REMAPCON function <https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-7330002.12.5>`_).
- Seven-day rolling accumulations are computed, with time axis labels denoting the start of each 7-day period. 

Filename conventions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each post-processed historical file, the following filename convention is used:

.. code-block:: linux
   
   <<variable>>_sevenday_<<weekly_statistic>>_<<year>>.nc

- **variable** (*str*): The requested variable (tas, mslp or pr).
- **weekly_statistic** (*str*): The statistic performed across a seven-day timescales. Options include:

  - ``'WEEKLYMEAN'``: Seven-day mean.
  - ``'WEEKLYSUM'``: Seven-day sum.

- **year** (int): The corresponding year associated with the dataset.

Summary
-------------
The following is a Python example that retrieves post-processed temperature, mean sea level pressure and precipitation data for 2005:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

   # Download temperature data
   tas_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'tas',password)
   # Download pressure data
   mslp_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'mslp',password)
   # Download precipitation data
   pr_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'pr',password)


