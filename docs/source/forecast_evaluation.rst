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

- **retrieve_weekly_obs**: Downloads weekly statistics of observed atmospheric characteristics ` (see :ref:`ADD SUBSECTION TITLE`).
- **retrieve_land_sea_mask**: Downloads land fraction values which are used to mask out oceanic grid points ` (see :ref:`ADD SUBSECTION TITLE`).
- **retrieve_20yr_quintile_clim**: Downloads climatological quintile boundaries which are compared against observed conditions ` (see :ref:`ADD SUBSECTION TITLE`). 

Evaluating a forecast locally
---------------------------------------------------
