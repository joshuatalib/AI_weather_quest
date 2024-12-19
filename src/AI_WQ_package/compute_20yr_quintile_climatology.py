# a script that computes the previous 20-year climatology from daily values.
import xarray as xr
import numpy as np
import pandas as pd

def complete_20yr_quintiles(da,initial_rolling_window=7,date_rolling_window=5):
    ''' Overarching function which calculates 20-year quintiles of rolling function for every year. 
    Variables: 
               da - DataArray to be processed.
               Initial_rolling_window (int) - The initial rolling-average taken, essentially set to seven for weekly-means.
               Date rolling window (int) - the number of points to sample. Set to 5. Similar to taking five hindcast sets.
    
    Return: A complete record of 20-year quintiles of five-day rolling means'''

    # determine years to find earliest year in dataset. basing it on years with January 1st
    jan_only = da['time'].sel(time=da['time'].dt.month == 1)
    min_year = jan_only.sel(time=jan_only['time'].dt.day == 1).dt.year.min().item()
    min_year_plus_20 = min_year+20
    # find max year - need 31st December
    dec_only = da['time'].sel(time=da['time'].dt.month == 12)
    max_year = dec_only.sel(time=dec_only['time'].dt.day == 31).dt.year.max().item()

    # create array with years to compute
    years_to_compute = range(min_year_plus_20,max_year)

    # set-up empty array
    doy_rolling_avgs = []

    for year in years_to_compute:
        print (year)
        # computes 20-year average of 5-day rolling mean
        doy_avg = compute_20yr_avg(da, year)
        # append the empty array
        doy_rolling_avgs.append(doy_avg)

    # Combine results into a single DataArray
    final_20yr_rolling_quin = xr.concat(doy_rolling_avgs, dim='time')

    return final_20yr_rolling_quin

# Function to compute the 20-year average for a specific year
def compute_20yr_avg(da, current_year, initial_rolling_window=7,date_rolling_window=5):
    ''' Function that computes 20-year quintiles of seven-day (week) rolling window. Will treat observational climatology in a similar manner to hindcast climatology. After taking 7-day rolling window, take a five day rolling window to average across multiple weeks. Seven-day rolling mean, and then five-day rolling-mean, is taken before computing average across the previous 20 years. 

    return: A full year of 20-year mean of rolling-mean values.
    '''

    # compute rolling mean on whole dataset. Uses function default value which is 7.
    weekly_rolling_mean = da.rolling(time=initial_rolling_window,center=False).mean()
    # then take five-day average of weekly rolling 
    five_avg_weekly_rolling_mean = weekly_rolling_mean.rolling(time=date_rolling_window,center=False).mean()

    # Exclude the current year and select 20 years before it
    start_year = current_year - 20
    subset = five_avg_weekly_rolling_mean.sel(time=(da['time'].dt.year >= start_year) & (da['time'].dt.year < current_year))

    # after computing a rolling mean across 5 days and selecting the previous 20 years, we defined a dayofyear series that is adjusted for leap years.
    # sort out treatment of leap years
    subset['time'] = pd.to_datetime(subset['time'])

    # original dayofyear
    subset['dayofyear'] = subset['time'].dt.dayofyear

    # create a is leap year field
    subset['is_leap_year'] = subset['time'].dt.is_leap_year
    # add 1 to dayofyear to dates after Feb 28th only in non-leap years
    # for all years we use leap year numbers and repeat Feb28th content for Feb 29th values. 

    subset['adjusted_dayofyear'] = subset['dayofyear'] + ((subset['dayofyear'] > 59) & ~subset['is_leap_year']).astype(int)

    # for non-leap years, repeat adjusted_day_of_year 59 and repeat for 60 (feb 29th)
    # Select rows for day 59 in non-leap years
    day_59_rows = subset[(subset['adjusted_dayofyear'] == 59) & ~subset['is_leap_year']].copy()

    # Set the adjusted_dayofyear to 60 for these duplicated rows
    day_59_rows['adjusted_dayofyear'] = 60

    # Append the duplicated rows back to the original dataset
    subset = xr.concat([subset, day_59_rows],dim='time')

    # Sort by adjusted_dayofyear and reset index for clean output
    subset = subset.sortby(['time'])

    # Compute the mean across the time dimension
    # please note, Feb 29th only takes average across leap years.
    doy_quin_20yr = subset.groupby('adjusted_dayofyear').quantile([0.2,0.4,0.6,0.8],dim='time')

    # define days for current year (will be dependent on leap year etc) and save to xarray.
    # for instance, if 2023 - save all days apart from DOY Feb 29th. 
    # if not a leap year, remove day 60 (Feb 29th) and subtract one off all dates afterwards.
    if current_year%4 != 0:
        # Mask out day 60 (February 29th) and adjust the remaining dayofyear
        # 1. Filter out February 29th
        data_no_feb29 = doy_quin_20yr.sel(adjusted_dayofyear=doy_quin_20yr.adjusted_dayofyear != 60)

        # 2. Adjust the `adjusted_dayofyear` coordinate for days after February 29th
        adjusted_dayofyear = data_no_feb29.adjusted_dayofyear.copy()
        adjusted_dayofyear = xr.where(adjusted_dayofyear > 60, adjusted_dayofyear - 1, adjusted_dayofyear)

        # 3. Assign the adjusted dayofyear coordinate back to the data array
        doy_quin_20yr = data_no_feb29.assign_coords(adjusted_dayofyear=adjusted_dayofyear)

    # have the final output with the correct data structure (current year, 1st Jan, 2nd Jan etc.)
    # create an array of dates using doy and current year
    dates = np.array([pd.Timestamp(current_year, 1, 1) + pd.Timedelta(days=int(d) - 1) for d in doy_quin_20yr['adjusted_dayofyear'].values])

    # assign new dates
    doy_quin_20yr = doy_quin_20yr.assign_coords(time=('adjusted_dayofyear', dates))

    # remove adjusted_dayofyear and use time instead
    doy_quin_20yr = doy_quin_20yr.swap_dims({"adjusted_dayofyear": "time"}).drop_vars("adjusted_dayofyear")

    return doy_quin_20yr



