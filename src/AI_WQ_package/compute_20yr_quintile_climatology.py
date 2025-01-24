# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

def complete_20yr_quintiles(da,initial_rolling_window=7,date_window=[-4,-2,0,2,4],rolling_operation='mean'):
    ''' Overarching function which calculates 20-year quintiles of rolling function for every year. 
    Variables: 
               da - DataArray to be processed.
               Initial_rolling_window (int) - The initial rolling-average taken, essentially set to seven for weekly-means.
               Date window (int) - the days to sample. Similar to taking five hindcast sets.
    
    Return: A complete record of 20-year quintiles of seven-day rolling means'''

    # find first timestep that you can commit 20-year climatology
    first_ts = pd.Timestamp(da['time'][0].values)
    first_20_clim_ts = first_ts + relativedelta(years=20) + relativedelta(days=float(date_window[-1])) # needs to be 20 years + 4 days from first timestep
    # find end 20 clim ts
    end_ts = pd.Timestamp(da['time'][-1].values)
    end_20_clim_ts = end_ts + relativedelta(years=1) - relativedelta(days=float(date_window[-1])) # add a year to the last date - two days.

    # create array with years to compute
    years_to_compute = range(first_20_clim_ts.year,end_20_clim_ts.year+1)

    # first compute weekly rolling mean or rolling sum for precip.
    if rolling_operation == 'mean':
        weekly_rolling = da.rolling(time=initial_rolling_window,center=False).mean()
    elif rolling_operation == 'sum':
        weekly_rolling = da.rolling(time=initial_rolling_window,center=False).sum()
    elif rolling_operation == 'none': # also given the option for none rolling, if it has already been performed. 
        weekly_rolling = da

    # set-up empty array
    doy_rolling_avgs = []

    for year in years_to_compute:
        print (year)
        # set the start and end dates dependent on whether in final year or not
        if year == first_20_clim_ts.year:
            start_date = first_20_clim_ts
        else:
            start_date = pd.Timestamp(f'{year}-01-01')
        if year == end_20_clim_ts.year:
            end_date = end_20_clim_ts
        else:
            end_date = pd.Timestamp(f'{year}-12-31')

        # computes 20-year average of 7-day rolling mean
        doy_avg = compute_20yr_avg(weekly_rolling, year,start_date,end_date,date_window=date_window)
        # append the empty array
        doy_rolling_avgs.append(doy_avg)

    # Combine results into a single DataArray
    final_20yr_rolling_quin = xr.concat(doy_rolling_avgs, dim='time')

    return final_20yr_rolling_quin

# Function to compute the 20-year average for a specific year
def compute_20yr_avg(weekly_means, current_year,start_date,end_date,date_window=[-4,-2,0,2,4]):
    ''' Function that computes 20-year quintiles of DataArray (should have already been given altered to a weekly-mean). Will treat observational climatology in a similar manner to hindcast climatology. After taking 7-day rolling window, take a five day rolling window to average across multiple weeks. Seven-day rolling mean, and then five-day rolling-mean, is taken before computing average across the previous 20 years. 

    return: A full year of 20-year mean of rolling-mean values.
    '''

    quintiles = []

    for date in pd.date_range(start=start_date, end=end_date, freq='D'):
        print (date)
        clim_data = []
        # go through all days in date window.
        for year_change in np.arange(-20,0): # go through past 20 years
            for day_change in date_window: # +/- 2 and 4 days - determined by date_rolling_window. 
                new_date = date + relativedelta(years=year_change) + relativedelta(days=float(day_change))
                clim_data.append(weekly_means.sel(time=new_date,method='nearest'))
        full_clim_set = xr.concat(clim_data,dim='time')
        # use full clim set (100 days), work out quintiles. need to rechunk due to dask handling
        quintile_clim = full_clim_set.chunk(dict(time=-1)).quantile(q=[0.2,0.4,0.6,0.8],dim='time')
        # add a time metric to quintile clim
        quintile_clim = quintile_clim.assign_coords(time=date)
        quintiles.append(quintile_clim)
    # after going through a full year, concate into a final xarray for that year.
    full_year_quintiles = xr.concat(quintiles,dim='time')

    return full_year_quintiles


