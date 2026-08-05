Training Data
======================================

Participants can use any observational, forecast or reanalysis dataset to develop their AI/ML sub-seasonal forecasting models. To facilitate initial model development, registered participants can download post-processed  `ERA5 <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview>`_ or `IBTrACS <https://www.ncei.noaa.gov/products/international-best-track-archive>`_ data. 

Accessing Available Data
--------------------------------------
The following datasets have been made easily accessible:

- Gridded `ERA5 <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview>`_ data at a 1.5 degree resolution:
   - Weekly-mean temperature (K)
   - Weekly-mean mean sea level pressure (Pa)
   - Weekly-accumulated total precipitation (mm week\ :sup:`-1`)

- `ERA5 <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview>`_-derived Madden-Julian Oscillation (MJO) characteristics, as well as Wheeler and Hendon (2004) combined EOFs and RMM standard deviations used for MJO projection and normalisation.
- `IBTrACS <https://www.ncei.noaa.gov/products/international-best-track-archive>`_ weekly-total of tropical storm days per defined basin. 

.. important::  
   
   Updates to ERA5 and IBTrACS-derived training data will be performed with a latency of three and twelve months respectively.  
Importing the Retrieve Training Data Module
--------------------------------------------
To download post-processed data, you will need functions from the `retrieve_training_data.py` module. The key function within this module is:

- **retrieve_annual_training_data**: Download annual files containing either: weekly statistics for temperature, mean sea level pressure or precipitation; daily MJO characteristics; or weekly totals of tropical storm days.

To import the necessary module, use the following Python code:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

Downloading Training Data
--------------------------------------------

Historical data, stored in annual files, can be retrieved using the `retrieve_annual_training_data` function:

.. code-block:: python

   retrieve_annual_training_data(<<year>>,<<variable>>,<<password>>,<<local_destination>>=None)

- **year** (*int*): The year of requested data, i.e. 2000. The year must be equal to or greater than 1979. 
- **variable** (*str*): The requested variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation
  - ``'MJO'``: MJO characteristics
  - ``'TS'``: TS days

- **password** (*str*): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded dataset. If unspecified, the dataset is saved within the working directory.

.. note::  
   
   The function only supports the variables listed above. Participants should ensure they have adequate storage space if downloading multiple years.

Additionally, MJO reference data based on Wheeler and Hendon (2004) can be retrieved using the `retrieve_MJO_projection_data` function:

.. code-block:: python

   retrieve_MJO_projection_data(<<password>>, <<local_destination>>=None)

- **password** (*str*): The forecast submission password provided in your registration email.
- **local_destination** (*str*): The local destination for the downloaded files. If unspecified, the files are saved within the working directory.

The function downloads the following files:

- ``WH04_combinedEOFs.nc``: The Wheeler and Hendon (2004) combined empirical orthogonal functions (EOFs) used to project daily anomalies onto the MJO phase space.
- ``WH04_RMM_stddevs.nc``: The observed standard deviations of RMM1 and RMM2 used to normalise the projected principal components.

The function returns a tuple containing the local paths to both downloaded files:

.. code-block:: python

   combined_EOFs_fn, RMM_stddevs_fn = retrieve_MJO_projection_data(password)

.. note::

   These files provide the observational reference data required to compute ERA5-derived or forecast-derived real-time multivariate MJO (RMM) indices
   using the methodology of Wheeler and Hendon (2004).


Understanding Data Processing Details
--------------------------------------------
Temperature and Pressure Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Downloaded at six-hourly intervals (0, 6, 12 and 18 UTC) at a 1.5 degree resolution.
- Seven-day rolling means are computed, with time axis labels indicating the start of each seven-day period. 

Precipitation Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Downloaded daily-accumulated 'total precipitation' at a 1.5 degree resolution using the following `tool <https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics?tab=download>`_.
- Daily accumulations are derived from hourly outputs of 12-hour background forecasts initialised at 0600 and 1800 UTC. 
- Seven-day rolling accumulations are computed, with time axis labels denoting the start of each seven-day period. 

MJO Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The MJO index is computed following the Wheeler and Hendon (2004) methodology, as implemented operationally by Gottschalck et al. (2010). Several differences have been made relative to Gottschalck et al. (2010), including the use of ERA5 reanalysis instead of NCEP–NCAR, no removal of harmonics associated with the seasonal cycle, and the use of a 1979 to 2025 climatological reference period to increase the sample size. Our methodology is summarised below:

- Downloaded daily-mean zonal wind at 850 hPa and 200 hPa (U850/U200), alongside top net longwave (thermal) radiation (ttr), at a 2.5 degree horizontal resolution using the following `tool <https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics?tab=download>`_. Zonal winds were extracted at a six-hourly resolution, whilst hourly accumulations of ttr were downloaded. Data was extracted over the full zonal band (−180 to 180 degrees longitude) and within ±15 degrees latitude. ttr was converted into outgoing longwave radiation (OLR) by multipling by -1.0 (positive values indicate outgoing radiation) and dividing by 3600.0 to convert from accumulated energy (J s-1) to radiative flux (W m-2).
- Subtracted the 1979 to 2025 day-of-year (DOY) climatology to compute daily anomalous fields. Note: The 29th February climatological value is constructed using 28th February values for non-leap years, ensuring a consistent sample size for all calendar days. We do not subtract harmonics associated with the seasonal cycle, as done in Gottschalck et al., 2010, as Lin et al. 2008 found that this is effectively performed in the next step when removing the previous 120-day average.
- Removed the preceding 120-day rolling-mean from each anomaly field to filter low-frequency (seasonal) variability. For example, values on 1st January 1981 have the mean between 3rd September to 31st December 1980 subtracted.
- Computed a cosine-weighted meridional mean over the ±15 degrees latitude band, resulting in 144 longitude points per day for each variable. Longitudes are defined on a regular −180 to 177.5 degree grid (2.5 degree spacing), without duplicated endpoints, and are treated as a cyclic zonal dimension when computing EOFs and projecting anomalies.
- Normalised each anomaly field using observed normalisation factors computed in Wheeler and Hendon (2004) using data from 1979 to 2001. Unlike the climatological anomalies, which are computed using a 1979 to 2025 reference period, the original Wheeler and Hendon (2004) normalisation factors are retained to ensure consistency with the published RMM methodology. Normalisation factors are 15.1 W m-2 for OLR, and 1.81 and 4.81 m s-1 for zonal wind at 850 and 200 hPa respectively. All normalisation factors can be downloaded using the *retrieve_MJO_projection_data* function.
- MJO characteristics are computed by projecting daily normalised ERA5 anomalies onto the observed climatological combined EOFs of Wheeler and Hendon (2004). Each computed PC index is normalised by observed standard deviations of RMM1 and RMM2. Combined EOFs used for MJO projection can be downloaded using the *retrieve_MJO_projection_data* function.

Individual MJO files contain the following diagnostics:
  - **RMM1 and RMM2**: The first two principal components obtained when projecting daily anomaly fields onto climatological EOF1 and EOF2.
  - **MJO amplitude**: Defined as sqrt(RMM1**2.0+RMM2**2.0)
  - **Phase angle**: The continuous angular position in (RMM1, RMM2) phase space. Phase angle is computed as arctan2(RMM2, RMM1).
  - **MJO phase (0-8)**: The discrete MJO phase as defined by Wheeler and Hendon (2004). When the MJO is inactive (amplitude < 1), the phase is set to zero. 

Tropical Storm Days Data Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Tropical storm (TS) activity is derived from the IBTrACS v4.01 dataset using three-hourly observations. Sub-daily storm track data is processed to produce weekly counts of TS presence within predefined ocean basins.

- Storm tracks are filtered to retain only observations with valid *usa_wind* values and wind speeds ≥ 17 m s⁻¹, consistent with the tropical storm threshold.

- Storms days are analysed across four ocean basins:
  
  - North Atlantic (ATL, 0° to 40°N, 100° to 20°W) 
  - North-West Pacific (NWP, 0° to 40°N, 100° to 180°E)
  - South-West Indian Ocean (SWIO, 0° to 40°S, 20° to 90°E) 
  - South-East Indian Ocean (SEIO, 0° to 40°S, 90° to 160°E)

- Three-hourly observations are aggregated to daily storm presence per ocean basin:
  
  - A day is classified as a storm day if at least one three-hourly record within that day satisfies the wind threshold.
  - Multiple qualifying observations of the same storm on a given day are counted as a single storm day, preventing double counting.

- A seven-day window is defined from the initial date. Daily storm presence is summed over seven days to compute the number of tropical storm days per basin per week.

.. note::  
   
    Unlike ERA5-derived variables, the tropical storm days diagnostic is produced with an approximately one-year latency, reflecting the extended time required to verify and consolidate tropical storm characteristics within the IBTrACS dataset.

Filename conventions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the exception of MJO characteristics, the following filename convention is used for each post-processed historical file:

.. code-block:: linux
   
   <<variable>>_sevenday_<<weekly_statistic>>_<<year>>.nc

- **variable** (*str*): The requested variable.
- **weekly_statistic** (*str*): The statistic performed across a seven-day timescales. Options include:

  - ``'WEEKLYMEAN'``: Seven-day mean.
  - ``'WEEKLYSUM'``: Seven-day sum.
  - ``'WEEKLYTSDAYS'``: Weekly totals of tropical storm days.

- **year** (int): The corresponding year associated with the dataset.

For daily MJO characteristics, the following filename convention is used:

.. code-block:: linux

   MJO_DAILY_<<year>>.nc

- **year** (int): The corresponding year associated with the dataset.

Summary
-------------
The following is a Python example that retrieves post-processed temperature, mean sea level pressure, precipitation, MJO and Tropical Storms days data for 2005:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data

   # Download temperature data
   tas_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'tas',<<password>>)
   # Download pressure data
   mslp_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'mslp',<<password>>)
   # Download precipitation data
   pr_2005 = retrieve_training_data.retrieve_annual_training_data(2005,'pr',<<password>>)
   # Download MJO data
   MJO_2025 = retrieve_training_data.retrieve_annual_training_data(2005,'MJO',<<password>>)
   # Download TS days data
   TS_2025 = retrieve_training_data.retrieve_annual_training_data(2005,'TS',<<password>>)

References
------------

Gottschalck, J., Wheeler, M., Weickmann, K., Vitart, F., Savage, N., Lin, H., Hendon, H., Waliser, D., Sperber, K., Prestrelo, C. and Nakagawa, M., 2010. A framework for assessing operational model MJO forecasts: a project of the CLIVAR Madden-Julian oscillation working group. Bull Am Meteorol Soc, 91(8), pp.1247-1258.

Lin, H., Brunet, G. and Derome, J., 2008. Forecast skill of the Madden–Julian oscillation in two Canadian atmospheric models. Monthly Weather Review, 136(11), pp.4130-4149.

Wheeler, M.C. and Hendon, H.H., 2004. An all-season real-time multivariate MJO index: Development of an index for monitoring and prediction. Monthly weather review, 132(8), pp.1917-1932.

