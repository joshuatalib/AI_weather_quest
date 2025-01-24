Submitting a Forecast
======================================

Importing Forecast Submission Functions
----------------------------------------
To submit a forecast to the AI Weather Quest, you will need to use key functions provided in the `forecast_submission.py` module of the `AI_WQ_package`. These functions leverage the `xarray` library to simplify forecast submissions.

Use the following line to import the necessary functions for forecast submission:

.. code-block:: python

   from AI_WQ_package import forecast_submission

Creating an Empty DataArray
---------------------------
To prepare your forecast submission, create an "empty" xarray DataArray. This template, with the necessary characteristics and attributes required for the AI Weather Quest, will be populated with forecasted probabilities to ensure compatibility with ECMWF IT infrastructure.

Use the `AI_WQ_create_empty_dataarray` function to generate a suitable DataArray:

.. code-block:: python

   AI_WQ_create_empty_dataarray(<<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>)

- **variable** (*str*): The forecasted variable. Options are:
  - `'tas'`: Near-surface temperature
  - `'mslp'`: Mean sea level pressure
  - `'pr'`: Precipitation
  
  *Note*: The function only works with these variables.

- **fc_start_date** (*str*): The forecast issue date in format `YYYYMMDD` (e.g., `'20250303'` for 3rd March 2025).

- **fc_period** (*str* or *int*): The chosen sub-seasonal forecasting period. Valid options are:
  - `'1'`: Weekly-mean forecasts for days 18 to 24 inclusive.
  - `'2'`: Weekly-mean forecasts for days 25 to 31 inclusive.
  
  *Note*: The function accepts either a string or integer. If an integer, it converts the variable to a string.

- **teamname** (*str*): The team name submitted during online registration.
- **modelname** (*str*): The model name submitted during online registration.

The function will only generate an empty DataArray if all parameters follow the required conventions. Ensure valid inputs to avoid errors.

**Example**:

.. code-block:: python

   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20241209', '1', 'EC', 'extrange')

This creates an empty DataArray for near-surface temperature predictions issued on 9th December 2024 for the first sub-seasonal forecasting period.

Empty DataArray Coordinates
---------------------------
Before populating the DataArray with forecasted probabilities, understand its coordinate structure:

- **Latitude**: Ranges from `90.0°N` to `-90.0°N` with a step of `-1.0°` latitude.
- **Longitude**: Ranges from `0.0°` to `359.0°` longitude with a step of `1.0°`.
- **Quintile**: Divided into intervals of `0.2` within `[0, 1.0]`. Quintile values represent the upper limit of climatological conditions:
  - `0.2`: Includes probabilities <= 0.2.
  - `0.4`, `0.6`, etc.: Include probabilities where the lower limit is the previous quintile value (e.g., `0.4` includes probabilities `0.2 <= x < 0.4`).

The DataArray also has coordinates describing the issuing forecast date and weekly forecast period. These time coordinates are stored in `np.datetime64` format.

When populating the DataArray with forecasted probabilities, adhere to these predefined coordinates to maintain compatibility with the AI Weather Quest submission process.

Populating the DataArray
------------------------
Once an "empty" DataArray is created and its structure is understood, fill the DataArray with forecast probabilities by assigning your data to its `values` attribute.

**Example**:

.. code-block:: python

   tas_p1_fc.values = forecast_array

Here, the `tas_p1_fc.values` attribute is filled with the data stored in `forecast_array`. The input array must have the shape `(5, 181, 360)` corresponding to the quintile, latitude, and longitude coordinates, respectively.

Submitting a Forecast to the AI Weather Quest
---------------------------------------------
Once you have populated the DataArray with forecast probabilities, you can submit your forecast to the AI Weather Quest. Use the `AI_WQ_forecast_submission` function:

.. code-block:: python

   AI_WQ_forecast_submission(<<populated_DataArray>>, <<password>>, <<variable>>, <<fc_start_date>>, <<fc_period>>, <<teamname>>, <<modelname>>)

**Parameters**:

- **populated_DataArray** (*xarray.DataArray*): The filled DataArray.
- **password** (*str*): The forecast submission portal password provided in your registration email.
- All other variables are the same as those used when creating the empty DataArray.

The function performs multiple checks to ensure suitable data formatting before submission. These checks include:

- The forecast issue date is within the four-day submission window (see forecast submission rules).
- Data shape is `(5, 181, 360)`.
- Latitude coordinate contains 181 points, ordered from `90.0°N` to `-90.0°N`.
- Longitude coordinate contains 360 points, ordered from `0.0°` to `359.0°`.
- Quintile coordinate has five values: `0.2`, `0.4`, `0.6`, `0.8`, and `1.0`.
- All data values are between `0.0` and `1.0`. (NaN values are permitted.)
- When summed across the first axis (the quintile axis), the total probability equals `1.0`.

After verification, the function populates a new DataArray that meets ECMWF requirements and transfers the forecasted probabilities to an ECMWF-hosted site. The returned DataArray is the one submitted.

**Example**:

.. code-block:: python

   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, password, 'tas', '20241209', '1', 'EC', 'extrange')

In this case, team `EC` has used the model `extrange` to predict near-surface temperatures for the first sub-seasonal forecasting period from 9th December 2024.

Summary
-------
Below is a complete Python code example for submitting a single forecast:

.. code-block:: python

   from AI_WQ_package import forecast_submission

   # Create an empty DataArray
   tas_p1_fc = forecast_submission.AI_WQ_create_empty_dataarray('tas', '20241209', '1', 'EC', 'extrange')

   # Populate the DataArray with forecast probabilities
   tas_p1_fc.values = tas_p1_fc_pbs

   # Submit the forecast
   tas_p1_fc_submit = forecast_submission.AI_WQ_forecast_submission(tas_p1_fc, password, 'tas', '20241209', '1', 'EC', 'extrange')

This process ensures your forecast is successfully transferred to the AI Weather Quest for real-time evaluation.
