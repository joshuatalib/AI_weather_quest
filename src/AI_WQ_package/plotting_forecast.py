# script to plot AI Weather Quest quintile probability forecast
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.feature as feature
import cartopy.crs as ccrs
import re
import xarray as xr
import numpy as np
import pandas as pd

def all_plot_choices(ax,i):
    ax.add_feature(feature.BORDERS,facecolor='none',edgecolor='black',linewidth=0.5)
    ax.add_feature(feature.LAND,facecolor='grey',edgecolor='black')
    ax.add_feature(feature.COASTLINE,facecolor='none',edgecolor='black')
    #ax.add_feature(feature.OCEAN, facecolor='white', edgecolor='black')
    ax.add_feature(feature.LAKES,edgecolor='black',linewidth=0.5)

    ax.set_xlim([-180.0,180.0])
    ax.set_ylim([-90.0,90.0])
    ax.set_xticks(np.linspace(-180,180,13))
    ax.set_yticks(np.linspace(-90.0,90.0,13))

    ax.set_xticklabels(np.linspace(-180.0,180.0,13))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%i'))
    ax.xaxis.set_minor_locator(MultipleLocator(5.0))
    ax.set_xlabel('Longitude ($^\circ$)')
    ax.set_xticklabels(np.linspace(-180.0,180.0,13))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%i'))

    ax.set_yticklabels(np.linspace(-90,90,13))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%i'))
    ax.yaxis.set_minor_locator(MultipleLocator(5.0))
    ax.set_ylabel('Latitude ($^\circ$)')
    ax.set_yticklabels(np.linspace(-90,90,13))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%i'))

def create_colormap():
    # create a colorbar
    levels = [0,3,6,9,12,15,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

    colors = [      '#2a2a2a',
                    '#36454F',
                    'grey',
                    'silver',
                    'gainsboro',
                    'white',
                    'mediumaquamarine',
                    'lightseagreen',
                    'cadetblue',
                    'steelblue',
                    'dodgerblue',
                    'royalblue',
                    'blue',
                    'darkblue',
                    'indigo',
                    'rebeccapurple',
                    'blueviolet',
                    'darkorchid',
                    'darkviolet',
                    'purple',
                    '#4b004b'
                    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("ai_wq_cmap",list(zip(np.linspace(0,1,len(colors)),colors)))

    norm = mcolors.BoundaryNorm(levels,cmap.N)
    return cmap, levels

def convert_long(lon):
    return np.where(lon > 180.0,lon-360,lon)

def get_forecast_attributes(single_quin):
    # function that gets all the attributes for figure title and savename
    quintile_value = single_quin.quintile.values
    # produce label to represent quintile range
    quintile_label = f'{round(quintile_value*100.0-20.0,1)} <= x < {round(quintile_value*100.0)}%'
    quintile_svename = f'{int(quintile_value*100.0)}'
    
    # standard name
    fc_standard_name = single_quin.standard_name
    # forecast periods
    fc_init_date = pd.Timestamp(single_quin.forecast_issue_date.values).strftime('%Y%m%d')
    fc_period_start = pd.Timestamp(single_quin.forecast_period_start.values).strftime('%Y%m%d')
    fc_period_end = pd.Timestamp(single_quin.forecast_period_end.values).strftime('%Y%m%d')
 
    # work out forecasting window
    leadtime = (pd.Timestamp(single_quin.forecast_period_start.values)-pd.Timestamp(single_quin.forecast_issue_date.values)).days
    if leadtime == 18:
        fcwin = '1'
    elif leadtime == 25:
        fcwin = '2'

    # get variable name, teamname and modelname from description
    description = single_quin.description
    pattern = r"(\w+) prediction from (\w+) using (\w+)"
    match = re.search(pattern, description)

    variable = match.group(1)
    teamname = match.group(2)
    modelname = match.group(3)

    # figure title
    fig_title = f'Probability of quintile range {quintile_label} for {fc_standard_name}. \n Forecast details: Initialisation date {fc_init_date}; forecast period: {fc_period_start} to {fc_period_end}; \n Teamname: {teamname}, Modelname: {modelname}.'
    sve_name = f'{variable}_{fc_init_date}_p{fcwin}_{teamname}_{modelname}_quintile_{quintile_svename}.jpg'

    return fig_title, sve_name

def plot_forecast(forecast,quintile_num,local_destination=None):
    # first sort longitude values so they plot -180 to 180
    forecast = forecast.assign_coords(longitude=(convert_long(forecast.longitude)))
    forecast = forecast.sortby('longitude')
    
    # from the forecast, select the quintile number
    single_quin = forecast.isel(quintile=int(quintile_num)-1)

    # get title and save names
    fig_title, sve_nme = get_forecast_attributes(single_quin)

    if local_destination:
        sve_nme = f'{local_destination}{sve_nme}'

    fig, ax = plt.subplots(1,1,figsize=[6.4,4.5],gridspec_kw=dict(hspace=0.0),subplot_kw=dict(projection=ccrs.PlateCarree()))
    # generate colormap  
    ai_wq_cmap, levels = create_colormap()
    # plot forecast
    CF = ax.contourf(single_quin.longitude,single_quin.latitude,single_quin*100.0,cmap=ai_wq_cmap,levels=levels)
    all_plot_choices(ax,0)
    ax.set_title(fig_title,fontsize=8.0)
    fig.subplots_adjust(bottom=0.15)
    cbar_ax = fig.add_axes([0.05,0.11,0.9,0.01])

    CB = plt.colorbar(CF,cax=cbar_ax,orientation='horizontal',pad=0.25,ticks=levels)
    CB.set_label('%')
    plt.savefig(sve_nme,dpi=200.0)
    plt.close()

