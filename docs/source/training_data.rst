Training Data
======================================

Participants are welcome to use any forecast or observational dataset to develop their AI/ML forecasting model. To support initial model development/training, post-processed ERA5 and MSWEP data is avaliable through the retrieve_training_data.py module. 

Importing Retrieve Training Data Functions
--------------------------------------------
To download post-processed ERA5 or MSWEP data, you will need key functions in the `retrieve_training_data.py` module. Important functions include:

- **retrieve_annual_training_data**: Download annual files containing weekly statistics of tas, mslp or pr.

Use the following python code to import functions within this module:

.. code-block:: python

   from AI_WQ_package import retrieve_training_data
