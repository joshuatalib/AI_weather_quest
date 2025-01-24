Forecast Evaluation
====================================

Three datasets are needed to evaluate a probabilistic sub-seasonal forecast:

1. The original probabilistic forecast;
2. Observations; and
3. A climatological set of probability limits.

Probabilistic Forecast
----------------------

Observations and Land-Sea Mask
------------------------------

The following script downloads the latest ERA5T and MSWEP data and transfers it to the FTP site.

**Script**: `download_observed_evaluation_data.bsh` [local machine]  
*(Note: Need to automate and work locally at ECMWF)*

```python
from AI_WQ_package import retrieve_evaluation_data

weekly_obs = retrieve_evaluation_data.retrieve_weekly_obs(<<date>>, <<variable>>, <<password>>)

land_sea_mask = retrieve_evaluation_data.retrieve_land_sea_mask(<<password>>)

Climatological quintile thresholds
----------------------------------
In the AI Weather Quest, climatological quintile thresholds are computed using ERA5 data for temperature and mean sea level pressure, while MSWEP data is used for precipitation. Quintile thresholds are crucial for forecast evaluation and can be leveraged by competitors to create probabilistic forecasts.

Climatological quintiles are calculated using observations from the previous 20 years within a 5-day window, which includes two days before and two days after the target date. For example, the climatological quintiles for 15th September 2024 are derived from data spanning the previous 20 years (2004 to 2023), covering the period from 13th to 17th September. The use of a five-day window increases our sample size to 100 observations. For leap day climatologies (February 29th), the 5-day window is adjusted to span from 26th February to 2nd March for non-leap years, and from 27th February to 2nd March for leap years. These quintiles are used to accurately evaluate forecasts and may serve as a reference for participants to make informed probabilistic predictions.



