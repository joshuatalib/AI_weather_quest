Training Data
======================================

Participants are welcome to use any forecast or observational dataset to develop their AI/ML forecasting model. To support initial model development/training, post-processed ERA5 and MSWEP data is avaliable through the retrieve_training_data.py module. Data through this module includes:

- Weekly-means of ERA5 temperature (K) and mean sea level pressure (Pa) spanning the period of 1979 to 2024.
- Weekly accumulations of MSWEP precipitation (mm day\ :sup:`-1`) covering the same period. 

Importing Retrieve Training Data Functions
--------------------------------------------
To download post-processed ERA5 or MSWEP data, you will need key functions in the `retrieve_training_data.py` module. Important functions include:

- **retrieve_annual_training_data**: Download annual files containing weekly statistics of tas, mslp or pr.

Use the following python code to import functions within this module:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data


Downloading Training Data
--------------------------------------------
Use the `retrieve_annual_training_data` function to download annual files contains weekly statistics of tas, mslp or pr:

.. code-block:: python

   retrieve_annual_training_data(<<year>>,<<variable>>,<<password>>)

- **year** (*str* or *int*): The year of requested data, i.e. '2000'.
- **variable** (*str*): The forecasted variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation

.. note::  
   
   The function only works with these variables.

- **password** (*str*): The forecast submission portal password provided in your registration email.

.. important::

   Each file is approximately 91 mb in size and contains weekly statistics at a daily, 1.5 degree resolution.

Summary
-------------
Below is a complete Python code example for retrieving post-processed temperature, mean sea level pressure and precipitation data for the year 2005:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

   # Download temperature data
   tas_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'tas',password)
   # Download pressure data
   mslp_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'mslp',password)
   # Download precipitation data
   pr_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'pr',password)


