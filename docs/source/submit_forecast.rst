Submitting a Forecast
======================================

Importing Forecast Submission Functions
----------------------------------------
To submit a forecast to the AI Weather Quest, you will need to use two key functions provided in the `forecast_submission.py` module of the `AI_WQ_package`. Important functions include:

- **AI_WQ_create_empty_dataarray**: Create an empty *xarray.DataArray* for forecast submission.
- **AI_WQ_forecast_submission**: Submit your populated *xarray.DataArray* to the AI Weather Quest.

Use the following line to import these necessary functions:

.. code-block:: python

   from AI_WQ_package import forecast_submission

Creating an Empty DataArray
---------------------------
To prepare your forecast submission, you will need to create an "empty" *xarray.DataArray* using the **AI_WQ_create_empty_dataarray** function. This function outputs an *xarray.DataArray* template that includes all the necessary characteristics and attributes required for the AI Weather Quest.

Use the `AI_WQ_create_empty_dataarray` function to generate a suitable DataArray:

.. code-block:: python

   AI_WQ_create_empty_dataarray(<<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>, <<password>>)

- **variable** (*str*): The forecasted variable. Options are:
  
  - ``'tas'``: Near-surface temperature
  - ``'mslp'``: Mean sea level pressure
  - ``'pr'``: Precipitation
  - ``'TS'``: Tropical storm days
  - ``'MJO'``: Madden-Julian Oscillation phase probabilities

- **fc_start_date** (*str*): The forecast initialisation date in format `YYYYMMDD` (e.g., `'20250515'` for 15th May 2025).

.. note::  
  
   The forecast initialisation date must correspond to a Thursday (see `forecast submission schedule <https://aiweatherquest.ecmwf.int/submitting-forecasts/>`__).

- **fc_period** (*str* or *int*): The selected forecasting window (`more details on the forecast submission schedule <https://aiweatherquest.ecmwf.int/submitting-forecasts/>`__). Valid options are:
  
  - ``'1'``: Weekly-mean forecasts for days 19 to 25 inclusive.
  - ``'2'``: Weekly-mean forecasts for days 26 to 32 inclusive.

.. note::  
  
   The function accepts either a string or integer. If an integer is provided, it is converted to a string. 

.. important::  
  
   For MJO forecasts this variable becomes redundant but still needed.

- **teamname** (*str*): Your team name.
- **modelname** (*str*): Your model name.

.. note::  
  
   Your latest team name and model name can be viewed on your team’s dashboard. 

- **password** (*str*): The forecast submission password provided in your registration email.

.. important::  
    
   On 13 August 2026, the AI Weather Quest will transition from an FTP service to ECBox. To ensure you can access ECBox, please use the password provided in the latest technical update email.

.. warning::

   The function will only generate an empty *DataArray* if all parameters follow the required conventions. Ensure valid inputs to avoid errors.

**Example**:

.. code-block:: python

   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20260813', '1', 'EC', 'extrange', <<password>>)

This creates an empty *DataArray* for near-surface (2 m) temperature predictions issued on 13th August 2026 for the first sub-seasonal forecasting window under the team name *EC* and associated with the model name *extrange*.

Understanding Empty DataArray Coordinates
-----------------------------------------
Before populating the empty *DataArray* with forecasted probabilities, you should understand key components of its coordinate structure. Below we outline specifics of each variable, however each *DataArray* also contains coordinates describing the forecast initialisation date and weekly forecast window. These time coordinates are stored in `np.datetime64` format.

.. important::

   When populating the *DataArray* with forecasted probabilities, adhere to these predefined coordinates to maintain compatibility with the AI Weather Quest submission process and plotting tools.

Global quintile-based probabilistic forecasts (tas, mslp and pr)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Latitude**: Ranges from `90.0°N` to `-90.0°N` with a step of `-1.5°` latitude.
- **Longitude**: Ranges from `0.0°` to `358.5°` longitude with a step of `1.5°`.
- **Quintile**: Divided into intervals of `0.2` within `[0, 1.0]`. Quintile values represent the upper limit of climatological conditions:

  - `0.2`: Includes probabilities < 0.2.
  - `0.4`, `0.6`, `0.8`: Include probabilities where the lower limit is the previous quintile value (e.g., `0.4` includes probabilities `0.2 <= x < 0.4`).
  - `1.0`: Includes probabilities >= 0.8.

The *DataArray* also has coordinates describing the forecast initialisation date and weekly forecast window. These time coordinates are stored in `np.datetime64` format.

Tercile-based probabilities of tropical storm days (TS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For tropical storm forecasts, the *DataArray* is structured to represent tercile-based probabilities of tropical storm days across predefined ocean basins.

The data has shape `(3, 4)`, corresponding to:

- 3 tercile categories (probability of occurrence)
- 4 ocean basins

The coordinate structure is as follows:

- **tercile**: Three equally spaced intervals representing three tercile categories. The coordinate values are `[0.33, 0.67, 1.0]`, used as labels for:

  - `0.33`: Lower tercile (below-normal conditions, < 0.33)
  - `0.67`: Middle tercile (near-normal conditions, 0.33 <= x < 0.66)
  - `1.0`: Upper tercile (above-normal conditions, >= 0.66)

  Each entry in this dimension contains the probability that tropical storm activity falls within the corresponding tercile category. Probabilities along the *tercile* dimension are expected to sum to one for each basin.

- **basin**: Fixed ocean basin regions where tropical storm activity is monitored. The supported basins are:

  - `ATL`: North Atlantic (0° to 40°N, 100° to 20°W)
  - `NWP`: Western North Pacific (0° to 40°N, 100° to 180°E)
  - `SWIO`: South-West Indian Ocean (0° to 40°S, 20° to 90°E)
  - `SEIO`: South-East Indian Ocean (0° to 40°S, 90° to 160°E)

.. note:: 

   For the Quest, tercile-based tropical storm day forecast probabilities are only evaluated during 13-week periods when each basin is climatologically active. These correspond to JJA and SON for the ATL and NWP basins, and DJF for the SWIO and SEIO basins.

Madden-Julian Oscillation phase probabilities (MJO)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For MJO forecasts, the *DataArray* is designed to store probabilistic predictions for each MJO phase at multiple forecast lead times.

The data has shape `(9, 4)`, corresponding to:

- 9 MJO phases
- 4 forecast lead times (days 8, 15, 22, and 29)

The coordinate structure is defined as follows:

- **MJO_phase**: Integer labels representing the standard Wheeler–Hendon MJO phase definition:

  - `0`: Inactive MJO
  - `1`–`8`: Active MJO phases 1 to 8

- **valid_time**: A sequence of valid forecast times corresponding to fixed lead times from the forecast issue date. These are provided as `np.datetime64` values and represent forecasts at days 8, 15, 22 and 29. Whilst we accept forecasts at week 1 and 2 lead times, only weeks 3 and 4 will be evaluated for public leaderboards.

Each element of the *DataArray* should contain the probability that the MJO is in a given phase at a given lead time. For each valid time, probabilities across the *MJO_phase* dimension are expected to sum to 1. These values can be subsequently visualised using Wheeler–Hendon phase-space diagrams via the *plot_MJO_forecast* function.

Populating the DataArray
------------------------
Once an empty *DataArray* is created and its structure is understood, fill the *xarray.DataArray* with forecasted probabilities by assigning your data to the `values` attribute.

**Example**:

.. code-block:: python

   tas_p1_fc.values = forecast_array

Here, the `tas_p1_fc.values` attribute is filled with the data stored in `forecast_array`. For global forecast variables (tas, mslp and pr), the input array must have the shape `(5, 121, 240)` corresponding to the quintile, latitude, and longitude coordinates respectively. For predictions of tropical storm days and MJO phase probabilities, the input arrays must have shape dimensions `(3,4)`, `(9,4)` respectively.

Submitting a Forecast to the AI Weather Quest
---------------------------------------------
Once you have populated the *DataArray* with forecasted probabilities, you can submit your forecast to the AI Weather Quest. Use the `AI_WQ_forecast_submission` function:

.. code-block:: python

   AI_WQ_forecast_submission(<<populated_DataArray>>, <<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>, <<password>>)

**Parameters**:

- **populated_DataArray** (*xarray.DataArray*): The filled *DataArray*.
- All other variables are the same as those used when creating the empty *DataArray*.

.. warning::

   The function will only permit submission if you provide the same teamname and modelname that was given during registration.

The function performs multiple checks to ensure suitable data formatting before submission. For all forecasts, the following checks are applied: 

- The forecast initialisation date must be a Thursday. Additionally, the time of submission must sit within the four-day submission window (see `forecast submission schedule <https://aiweatherquest.ecmwf.int/submitting-forecasts/>`__). 
- All data values must lie between `0.0` and `1.0` (NaNs are also permitted).

For global variables (*tas*, *mslp*, *pr*), additional checks include:

- Data shape is `(5, 121, 240)`.
- Latitude coordinate contains 121 points, ordered from `90.0°N` to `-90.0°N`.
- Longitude coordinate contains 240 points, ordered from `0.0°` to `358.5°`.
- Quintile coordinate has five values: `0.2`, `0.4`, `0.6`, `0.8`, and `1.0`.
- When summed across the first axis (the quintile axis), the total probability equals `1.0`.  

For tropical storm (*TS*) forecasts:

- Data shape is `(3,4)`, corresponding to 3 tercile categories and 4 ocean basins.
- The tercile coordinate contains three values: 0.33, 0.67, and 1.0.
- When summed across the first axis (the tercile axis), the total probability equals 1.0 for active basins during the relevant 13-week period.

For *MJO* forecasts:

- Data shape is `(9,4)`, corresponding to 9 MJO phases and 4 forecast lead times.
- The MJO_phase coordinate contains 9 integer values: 0 (inactive) and 1 to 8 (active phases).
- When summed across the first axis (the MJO_phase axis), the total probability equals 1.0.

After verification, the function returns a validated *xarray.DataArray* and generates the corresponding submission filename. The *DataArray* conforms to ECMWF submission requirements and can then be transferred to the ECMWF-hosted ECBox service.

.. note::

   When you submit a forecast, it will be assigned an *origin* ID and an *expver* ID:
      - The origin ID is derived from the first four and last two characters of your team name, followed by a two-digit number.
      - The expver ID consists of your full team name followed by a two-digit number.

**Example**:

.. code-block:: python

   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, 'tas', '20260813', '1', 'EC', 'extrange', <<password>>)

In this case, team `EC` has used the model `extrange` to predict near-surface temperatures for the first sub-seasonal forecasting period (days 19 to 25) from 13th August 2026.

Checking for a Successful Forecast Submission
---------------------------------------------
You can check whether your forecast has been successfully submitted to the AI Weather Quest by using the forecast_submission.AI_WQ_check_submission function. This function validates your registration details and confirms if a submitted forecast is present.

.. code-block:: python

   AI_WQ_check_submission(<<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>, <<password>>)

**Parameters**:

- All variables are the same as those used when creating the empty *DataArray*.

The function will print out three lines. The first and second will state whether the teamname and modelname is registered to the AI Weather Quest, respectively, whilst the third will inform you whether your file has been successfully submitted to the Quest. If there is an issue, the third line will display an error message. The common issues will be:

- If the file does not exist.
- If the forecast initialisation date is invalid, and the directory is not found.

**Example**:

.. code-block:: python

   from AI_WQ_package.forecast_submission import AI_WQ_check_submission
   AI_WQ_check_submission('tas','20250717','1','ECMWFtest','dynamicalEC',password)

Output:

.. code-block::

   ECMWFtest is registered to the AI Weather Quest. You may submit your forecast.
   dynamicalEC is registered to the AI Weather Quest. You may submit your forecast.
   File 'tas_20250717_p1_ECMWFtest_dynamicalEC.nc' exists. You have successfully submitted to the AI Weather Quest

Summary
-------
Below is a complete Python code example for submitting a single forecast:

.. code-block:: python

   from AI_WQ_package import forecast_submission

   # Create an empty DataArray
   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20260813', '1', 'EC', 'extrange', <<password>>)

   # Populate the DataArray with forecast probabilities
   tas_p1_fc.values = tas_p1_fc_pbs

   # Submit the forecast
   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, 'tas', '20260813', '1', 'EC', 'extrange', <<password>>)

This process ensures your forecast is successfully transferred to the AI Weather Quest for real-time evaluation.
