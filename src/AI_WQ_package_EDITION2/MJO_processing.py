# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

# python script that 20 year climatology of MJO probabilities
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys

def compute_20yr_MJOprob_climatology(MJO_phase_timeseries,date_str,savedir,
                                     lower_year_limit=-20,upper_year_limit=-1,
                                     chosen_day_diff=[-4,-2,0,2,4]):
    """
    Function that computes climatological MJO probabilities for a specific day (date str).

    MJO_phase_timeseries: historical time series of MJO phases.
    date_str = YYYYMMDD date format to compute MJO probabilities
    savedir: location to save MJO probabilities
    """

    print (f'Computing MJO phase probabilities for {date_str}')
    
    date = datetime.strptime(date_str,'%Y%m%d')
    
    # reduce number of years for quick processing (stuck to lower_year_limit-1 and 0 in case of overlap into previous year, i.e. Dec to Jan)
    # loading in 21 years but only sampling 20 years
    fc_year = date.year
    lower_year = fc_year+lower_year_limit-1
    upper_year = fc_year+upper_year_limit+1 # also keep following year, as the +4 can mean dates go into following year

    # need to reduce MJO timeseries
    MJO_phases = MJO_phase_timeseries.where(
                 (MJO_phase_timeseries['time'].dt.year >= lower_year) &
                 (MJO_phase_timeseries['time'].dt.year <= upper_year),
                 drop=True)

    MJO_day_samples = []
    # loop through climatology (i.e. previous 20 years, +/- 4 days)
    for year_diff in range(lower_year_limit,upper_year_limit+1): # year diff
        for day_diff in chosen_day_diff: # day diff
            # get start date of week for chosen year
            lagged_date = date + relativedelta(years=year_diff) + relativedelta(days=day_diff)
            MJO_phase_single_day = MJO_phases.sel(time=lagged_date)
            MJO_day_samples.append(MJO_phase_single_day)

    # all MJO days
    all_sampled_MJO = xr.concat(MJO_day_samples,dim='time')
     
    # percentages for each phase
    percentages = []
    for phase in np.arange(9):
        perc = all_sampled_MJO[all_sampled_MJO==phase].count()/all_sampled_MJO.count()
        percentages.append(perc.values)
    percentages = np.asarray(percentages) 

    # populate MJO probability xarray, (phase)
    # add shortName
    shortName = 'MJOphase'
    # work out forecast issue time
    date_iso = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    single_time = np.datetime64(date_iso + "T00:00:00")
    
    # save dataarray
    da = xr.DataArray(data=percentages[None, :],   # shape (1, phase)
                      dims=['time', 'MJO_phase'],
                      coords=dict(time=[single_time],MJO_phase=np.arange(9)),
    attrs=dict(Conventions='CF-1.6',shortName=shortName,
               units='MJO_climatological_probabilities'))
    da.name = "MJO_clim_prob"
    da.to_netcdf(f"{savedir}/MJO_20yrCLIM_DAILYprobs_{date_str}.nc") # save the file
    return da
