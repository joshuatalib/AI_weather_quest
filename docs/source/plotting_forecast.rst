Forecast Plotting
====================================

Importing the Forecast Plotting Module
----------------------------------------

To help participants visualize their sub-seasonal forecasts, the *AI-WQ-Package* includes a dedicated module called **plotting_forecast**. This module allows you to easily plot global probabilistic forecasts.

To import the necessary plotting function, use:

.. code-block:: python

  from AI_WQ_package.plotting_forecast import plot_forecast

Plotting a forecast
---------------------------------------

The *plot_forecast* function generates a map showing the probability forecast for a given quantile range. The resulting figure matches the format used on the AI Weather Quest Forecast Portal.

The *plot_forecast* function only has three inputs:

.. code-block:: python

  plot_forecast(<<forecast>>,<<quintile_num>>,local_destination=None)

- **forecast** (*xarray.dataarray*): Your submitted forecast to the AI Weather Quest.
- **quintile_num** (*int* or *str*): The selected quintile where 1 refers to  < 20%, 2 refers to 20 <= x < 40% etc.
- **local_destination** (*str*, optional): Path to the local folder where the figure will be saved. If not provided, the figure will be saved in the current working directory.

The figure filename is automatically created using forecast attributes. The format is:

.. code-block:: python
    
    <<variable>>_<<fc_init_date}>>_p<<fcwin>>_<<teamname>>_<<modelname>>_quintile_<<quintile_value>>.jpg

where:

- **variable**: Forecasted variable (e.g. tas, mslp or pr).
- **fc_init_date**: Forecast initialisation date in format *YYYYMMDD* (e.g. 20250403).
- **fcwin**: The sub-seasonal forecasting window (either '1' or '2').
- **teamname**: The teamname associated with the submitted forecast.
- **modelname**: The modelname associated with the submitted forecast.
- **quintile_value**: Upper limit of the selected quintile (e.g. 20, 40 etc.)

.. note::  
   
   The *plot_forecast* function only works with dataarray templates provided through the *AI-WQ-package*.

Example Usage
---------------------------------------

Here is how you might use the function to generate a forecast plot for the 60–80% quintile range:

.. code-block:: python

  from AI_WQ_package.plotting_forecast import plot_forecast
  
  # Plot the 4th quintile (60 to 80%) and save to a local folder ('/home/test_figures/')
  plot_forecast(submitted_forecast,4,local_destination='/home/test_figures/'
