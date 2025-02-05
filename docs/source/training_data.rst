Training Data
======================================

Participants can use any available forecast or observational dataset to develop their AI/ML forecasting models. To facilitate initial model development/training, registered participants can download post-processed ERA5 and MSWEP data through the retrieve_training_data.py module. 

Avaliable Data
--------------------------------------
The following datasets are avaliable through the retrieve_training_data.py module:

- ERA5 data (1979 - 2024):
   - Weekly-mean temperature (K)
   - Weekly-mean mean sea level pressure (Pa)
- MSWEP data (1979 - 2024):
   - Weekly-accumulated precipitation (mm week\ :sup:`-1`)

Importing Functions from the Retrieve Training Data Module
--------------------------------------------
To download post-processed ERA5 or MSWEP data, you will need functions from the `retrieve_training_data.py` module. The key function within this module is:

- **retrieve_annual_training_data**: Download annual files containing weekly statistics for temperature (tas), mean sea level pressure (mslp) or precipitation (pr).

To import the module, use the following Python code:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data


Downloading Training Data
--------------------------------------------
To download data to the directory you are working in, use the `retrieve_annual_training_data` function:

.. code-block:: python

   retrieve_annual_training_data(<<year>>,<<variable>>,<<password>>)

- **year** (*str* or *int*): The year of requested data, i.e. '2000'.
- **variable** (*str*): The forecasted variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

- **password** (*str*): The forecast submission portal password provided in your registration email.

.. note::  
   
   The function only supports the variables listed above.

.. important::

   Each file is approximately 91 MB and contains weekly statistics at a daily, 1.5 degree resolution. Participants should ensure they have adequate storage space if downloading data for multiple years.

Data Processing Details
--------------------------------------------
ERA5 Data Processing

- Downloaded at six-hourly intervals (0, 6, 12 and 18 UTC) at a 1.5 degree resolution.
- Seven-day rolling means are computed, with time axis labels indicating the start of each 7-day period. 

MSWEP Data Processing

- Data before 2021 was sourced from the *Past* directory, whilst data from 2021 onwards is from the *NRT* directory. 
- Daily rainfall accumulations are regridded to a 1.5-degree resolution using first-order conservative remapping (`CDO REMAPCON function <https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-7330002.12.5>`_).
- Seven-day rolling sums are computed, with time axis labels denoting the start of each 7-day period. 

Summary
-------------
The following is a Python example that retrieves post-processed temperature, mean sea level pressure, and precipitation data for 2005:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

   # Download temperature data
   tas_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'tas',password)
   # Download pressure data
   mslp_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'mslp',password)
   # Download precipitation data
   pr_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'pr',password)


