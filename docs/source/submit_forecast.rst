Submitting a Forecast
======================================

Importing Forecast Submission Functions
----------------------------------------
To submit a forecast to the AI Weather Quest, you will need to use two key functions provided in the `forecast_submission.py` module of the `AI_WQ_package`. Important functions include:

- **AI_WQ_create_empty_dataarray**: Create an empty *xarray.DataArray* for forecast submission.
- **AI_WQ_forecast_submission**: Submit your populated DataArray to the AI Weather Quest.

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

- **fc_start_date** (*str*): The forecast initialisation date in format `YYYYMMDD` (e.g., `'20250515'` for 15th May 2025).

.. note::  
  
   To create an empty *xarray.DataArray*, a forecast initialisation date that occurs on a Thursday must be given. 

- **fc_period** (*str* or *int*): The selected forecasting window (`more details on the forecast submission schedule <https://aiweatherquest.ecmwf.int/submitting-forecasts/>`__). Valid options are:
  
  - ``'1'``: Weekly-mean forecasts for days 19 to 25 inclusive.
  - ``'2'``: Weekly-mean forecasts for days 26 to 32 inclusive.

.. note::  
  
   The function accepts either a string or integer. If an integer is provided, it is converted to a string. 

- **teamname** (*str*): Your team name.
- **modelname** (*str*): Your model name.

.. note::  
  
   Your latest team name and model name can be viewed on your team’s login page with the credentials provided by email upon registration. 

- **password** (*str*): The forecast submission password provided in your registration email.

.. warning::

   The function will only generate an empty *DataArray* if all parameters follow the required conventions. Ensure valid inputs to avoid errors.

**Example**:

.. code-block:: python

   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20241209', '1', 'EC', 'extrange', <<password>>)

This creates an empty DataArray for near-surface (2 m) temperature predictions issued on 9th December 2024 for the first sub-seasonal forecasting window under the team name *EC* and associated with the model name *extrange*.

Understanding Empty DataArray Coordinates
-----------------------------------------
Before populating the empty *DataArray* with forecasted probabilities, you should understand key components of its coordinate structure:

- **Latitude**: Ranges from `90.0°N` to `-90.0°N` with a step of `-1.5°` latitude.
- **Longitude**: Ranges from `0.0°` to `358.5°` longitude with a step of `1.5°`.
- **Quintile**: Divided into intervals of `0.2` within `[0, 1.0]`. Quintile values represent the upper limit of climatological conditions:

  - `0.2`: Includes probabilities < 0.2.
  - `0.4`, `0.6`, `0.8`: Include probabilities where the lower limit is the previous quintile value (e.g., `0.4` includes probabilities `0.2 <= x < 0.4`).
  - `1.0`: Includes probabilities >= 0.8.

The DataArray also has coordinates describing the forecast initialisation date and weekly forecast window. These time coordinates are stored in `np.datetime64` format.

.. important::

   When populating the DataArray with forecasted probabilities, adhere to these predefined coordinates to maintain compatibility with the AI Weather Quest submission process.

Populating the DataArray
------------------------
Once an empty *DataArray* is created and its structure is understood, fill the *xarray.DataArray* with forecasted probabilities by assigning your data to the `values` attribute.

**Example**:

.. code-block:: python

   tas_p1_fc.values = forecast_array

Here, the `tas_p1_fc.values` attribute is filled with the data stored in `forecast_array`. The input array must have the shape `(5, 121, 240)` corresponding to the quintile, latitude, and longitude coordinates respectively.

Submitting a Forecast to the AI Weather Quest
---------------------------------------------
Once you have populated the DataArray with forecasted probabilities, you can submit your forecast to the AI Weather Quest. Use the `AI_WQ_forecast_submission` function:

.. code-block:: python

   AI_WQ_forecast_submission(<<populated_DataArray>>, <<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>, <<password>>)

**Parameters**:

- **populated_DataArray** (*xarray.DataArray*): The filled DataArray.
- All other variables are the same as those used when creating the empty DataArray.

.. warning::

   The function will only permit submission if you provide the same teamname and modelname that was given during registration.

The function performs multiple checks to ensure suitable data formatting before submission. These checks include:

- That the forecast initialisation date is a Thursday and within the four-day submission window (see `forecast submission schedule <https://aiweatherquest.ecmwf.int/submitting-forecasts/>`__).
- Data shape is `(5, 121, 240)`.
- Latitude coordinate contains 121 points, ordered from `90.0°N` to `-90.0°N`.
- Longitude coordinate contains 240 points, ordered from `0.0°` to `358.5°`.
- Quintile coordinate has five values: `0.2`, `0.4`, `0.6`, `0.8`, and `1.0`.
- All data values are between `0.0` and `1.0` (NaN values are also permitted).
- When summed across the first axis (the quintile axis), the total probability equals `1.0`.

After verification, the function populates a new *xarray.DataArray* that meets ECMWF requirements and transfers forecasted probabilities to an ECMWF-hosted site. The returned DataArray is the one that has been submitted to the competition.

.. note::

   When you submit a forecast, it will be assigned an *origin* ID and an *expver* ID:
      - The origin ID is derived from the first four and last two characters of your team name, followed by your model submission number.
      - The expver ID consists of your full team name followed by your model submission number.
   On the ECMWF-hosted sub-seasonal forecast portal, your forecast will be identified by the expver ID. Additionally, a temporary *netcdf* file will be saved in your working directory during submission. 

**Example**:

.. code-block:: python

   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, 'tas', '20241209', '1', 'EC', 'extrange', <<password>>)

In this case, team `EC` has used the model `extrange` to predict near-surface temperatures for the first sub-seasonal forecasting period (days 19 to 25) from 9th December 2024.

Summary
-------
Below is a complete Python code example for submitting a single forecast:

.. code-block:: python

   from AI_WQ_package import forecast_submission

   # Create an empty DataArray
   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20241209', '1', 'EC', 'extrange', <<password>>)

   # Populate the DataArray with forecast probabilities
   tas_p1_fc.values = tas_p1_fc_pbs

   # Submit the forecast
   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, 'tas', '20241209', '1', 'EC', 'extrange', <<password>>)

This process ensures your forecast is successfully transferred to the AI Weather Quest for real-time evaluation.
