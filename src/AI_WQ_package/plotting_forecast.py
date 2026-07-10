# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

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
import os
from datetime import datetime, timedelta
from AI_WQ_package import retrieve_training_data, retrieve_evaluation_data

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
    ax.set_xlabel(r'Longitude ($^\circ$)')
    ax.set_xticklabels(np.linspace(-180.0,180.0,13))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%i'))

    ax.set_yticklabels(np.linspace(-90,90,13))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%i'))
    ax.yaxis.set_minor_locator(MultipleLocator(5.0))
    ax.set_ylabel(r'Latitude ($^\circ$)')
    ax.set_yticklabels(np.linspace(-90,90,13))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%i'))

def create_colormap():
    # create a colorbar
    levels = [0,3,6,9,12,15,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

    colors = [      '#2a2a2a',
                    '#36454F',
                    'slategray',
                    'darkgray',
                    'gainsboro',
                    'lightgrey',
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

def calc_fcwin(fc):
    leadtime = (pd.Timestamp(fc.forecast_period_start.values)-pd.Timestamp(fc.forecast_issue_date.values)).days
    if leadtime == 18:
        fcwin = '1'
    elif leadtime == 25:
        fcwin = '2'
    return fcwin

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
    fcwin = calc_fcwin(single_quin)
    #leadtime = (pd.Timestamp(single_quin.forecast_period_start.values)-pd.Timestamp(single_quin.forecast_issue_date.values)).days
    #if leadtime == 18:
    #    fcwin = '1'
    #elif leadtime == 25:
    #    fcwin = '2'

    # get variable name, teamname and modelname from description
    description = single_quin.description
    pattern = r"(\w+) prediction from (\w+) using (\w+)"
    match = re.search(pattern, description)

    variable = match.group(1)
    teamname = match.group(2)
    modelname = match.group(3)

    # figure title
    fig_title = f'Probability of quintile range {quintile_label} for {fc_standard_name}. \n Forecast details: Initialisation date {fc_init_date}; forecast period: {fc_period_start} to {fc_period_end}.\n Teamname = {teamname}, Modelname = {modelname}'
    sve_name = f'{variable}_{fc_init_date}_p{fcwin}_{teamname}_{modelname}_quintile_{quintile_svename}.jpg'

    return fig_title, sve_name

def plot_forecast(forecast,quintile_num,local_destination=None,format='jpg'):
    # first sort longitude values so they plot -180 to 180
    forecast = forecast.assign_coords(longitude=(convert_long(forecast.longitude)))
    forecast = forecast.sortby('longitude')
    
    # from the forecast, select the quintile number
    single_quin = forecast.isel(quintile=int(quintile_num)-1)

    # get title and save names
    fig_title, sve_nme = get_forecast_attributes(single_quin)

    if local_destination:
        sve_nme = f'{local_destination}{sve_nme}'

    # assign format
    root, ext = os.path.splitext(sve_nme) # split the filename
    sve_nme = f"{root}.{format.lstrip('.')}" # take the root and add chosen format onto end


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

#####
# MJO functions
#####

def create_MJO_colormap():
    # create a colorbar
    levels = [0,1,2,3,4,5,10,15,20,25,30,35,40,45,50,55,60,65,70,80,90,100]

    colors = [      '#2a2a2a',
                    '#36454F',
                    'slategray',
                    'darkgray',
                    'gainsboro',
                    'lightgrey',
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
    norm = mcolors.BoundaryNorm(levels, cmap.N)
    return cmap, levels, norm

def draw_wh_diagram(ax, percentages, title=''):
    """
    Draw a Wheeler–Hendon phase diagram with sector colouring.

    Parameters
    ----------
    ax : matplotlib axis
        Axis on which to draw the WH diagram.
    percentages : data
        Values are percentages (0–100).
    title : str
        Panel title.
    """

    # Order of sectors: inactive (center) then phases 1–8
    phases = ['inactive'] + list(range(1, 9))
    vals = percentages

    # Normalise for colormap
    cmap, levels, norm = create_MJO_colormap()

    # Plot limits
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)

    # Phase box coordinates (classic WH layout)
    # Large 8 sectors approximated as 8 rectangular regions
    phase_boxes = {
        1: (-4, 0, 4, 4),    # RMM1<0, RMM2>0
        2: (-4, 0, 0, 4),
        3: (0, 0, 4, 4),
        4: (0, -4, 4, 0),
        5: (0, -4, 4, 0),
        6: (-4, -4, 0, 0),
        7: (-4, -4, 0, 0),
        8: (0, 0, 4, 4),
    }

    # Correct “pie slice” style Cartesian phase definition:
    # (the real WH diagram uses radial angles; this is the faithful version)
    wh_phase_angles = {
        5: (0, 45),
        6: (45, 90),
        7: (90, 135),
        8: (135, 180),
        1: (-180, -135),
        2: (-135, -90),
        3: (-90, -45),
        4: (-45, 0)
    }

    # Draw phase labels in polar style
    for phase, ang_range in wh_phase_angles.items():
        ang = np.deg2rad(np.mean(ang_range))
        x = 3.5 * np.cos(ang)
        y = 3.5 * np.sin(ang)
        t = ax.text(x, y, f"{phase}", ha='center', va='center', fontsize=10, fontweight='bold')
        t.set_bbox(dict(boxstyle="round,pad=0.25",facecolor="white",edgecolor="black",linewidth=0.8,alpha=0.9))

    # Draw shaded sectors
    for phase in range(1, 9):
        ang1, ang2 = np.deg2rad(wh_phase_angles[phase])

        # Use wedge-like shading but clipped inside the square
        theta = np.linspace(ang1, ang2, 50)
        r = 8
        xs = np.concatenate([[0], r*np.cos(theta), [0]])
        ys = np.concatenate([[0], r*np.sin(theta), [0]])

        col = cmap(norm(vals[phase]))
        ax.fill(xs, ys, color=col, alpha=1.0,edgecolor='black',linewidth=1.0)

        # Annotate percentage
        ang_mid = np.deg2rad(np.mean(wh_phase_angles[phase]))
        t = ax.text(2.2*np.cos(ang_mid),
                2.2*np.sin(ang_mid),
                f"{vals[phase]:.1f}%",
                ha='center', va='center', fontsize=12)
        t.set_bbox(dict(boxstyle="round,pad=0.25",facecolor="white",edgecolor="black",linewidth=0.8,alpha=0.9))

    # Inactive region = circle near origin
    inactive_val = vals[0]
    ax.add_patch(plt.Circle((0, 0), 1.0,
                            facecolor='white',
                            alpha=1.0,edgecolor='black',linewidth=1.0))
    t = ax.text(0, 0.3, f"{inactive_val:.1f}%", ha='center', va='center', fontsize=12)
    t.set_bbox(dict(boxstyle="round,pad=0.25",facecolor="white",edgecolor="black",linewidth=0.8,alpha=0.9))
    t = ax.text(0, -0.3, "Inactive", ha='center', va='center', fontsize=10,fontweight='bold')
    t.set_bbox(dict(boxstyle="round,pad=0.25",facecolor="white",edgecolor="black",linewidth=0.8,alpha=0.9))

    # Axes & styling
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.set_title(title)

def get_MJO_forecast_attributes(forecast):
    # get attributes from forecast file
    fc_init_date = pd.Timestamp(forecast.forecast_issue_date.values).strftime('%Y%m%d')
    teamname = forecast.teamname
    modelname = forecast.modelname

    fig_title = f'Probability for each MJO phase\nForecast details: Initialisation date {fc_init_date}\nTeamname: {teamname}; Modelname: {modelname}'

    sve_name = f'MJO_{fc_init_date}_{teamname}_{modelname}.jpg'

    return fig_title, sve_name

def plot_MJO_forecast(forecast,local_destination=None,format='jpg'):
    fig_title, sve_nme = get_MJO_forecast_attributes(forecast)
    if local_destination:
        sve_nme = f'{local_destination}{sve_nme}'
    # assign format
    root, ext = os.path.splitext(sve_nme) # split the filename
    sve_nme = f"{root}.{format.lstrip('.')}" # take the root and add chosen format onto end

    # make panel titles
    panel_titles = []
    for time in forecast.valid_time:
        lead_time = time-forecast.forecast_issue_date
        lead_time_days = lead_time.astype('timedelta64[D]').item().days
        panel_titles.append(f"Lead time: {lead_time_days} days. Valid date: {pd.to_datetime(time.values).strftime('%Y%m%d')}")

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    for ax, data, title in zip(axes.flatten(), np.transpose(forecast.values)*100,
                           panel_titles):
        draw_wh_diagram(ax, data, title=title)

    plt.suptitle(fig_title)

    cmap, levels, norm = create_MJO_colormap()
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    cbar_ax = fig.add_axes([0.05,0.05,0.9,0.02])
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),cax=cbar_ax,orientation='horizontal',ticks=levels)
    cb.set_label('%')
    #plt.tight_layout()
    plt.savefig(sve_nme,dpi=200.0)
    plt.close()

######
## TS activity functions
######

def create_TS_colormap():
    # create a colorbar
    levels = [0,5,10,15,20,25,40,45,50,55,60,65,70,75,80,85,90,95,100]

    colors = [      '#2a2a2a',
                    '#36454F',
                    'slategray',
                    'darkgray',
                    'gainsboro',
                    'lightgrey',
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
                    'darkorchid'
                    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("ai_wq_cmap",list(zip(np.linspace(0,1,len(colors)),colors)))
    norm = mcolors.BoundaryNorm(levels, cmap.N)
    return cmap, levels, norm

def get_TS_forecast_attributes(forecast):
    # get attributes from forecast file
    fc_init_date = pd.Timestamp(forecast.forecast_issue_date.values).strftime('%Y%m%d')
    teamname = forecast.teamname
    modelname = forecast.modelname

    fig_title = f'Tercile-based probabilities for Tropical Storm number\nForecast details: Initialisation date {fc_init_date}\nTeamname: {teamname}; Modelname: {modelname}'

    sve_name = f'TS_{fc_init_date}_{teamname}_{modelname}.jpg'

    return fig_title, sve_name

def all_plot_choices_TS(ax):
    ax.add_feature(feature.BORDERS,facecolor='none',edgecolor='black',linewidth=0.5,transform=ccrs.PlateCarree(central_longitude=180.0))
    ax.add_feature(feature.LAND,facecolor='grey',edgecolor='black',transform=ccrs.PlateCarree(central_longitude=180.0))
    ax.add_feature(feature.COASTLINE,facecolor='none',edgecolor='black',transform=ccrs.PlateCarree(central_longitude=180.0))
    #ax.add_feature(feature.OCEAN, facecolor='white', edgecolor='black')
    ax.add_feature(feature.LAKES,edgecolor='black',linewidth=0.5,transform=ccrs.PlateCarree(central_longitude=180.0))

    ax.set_global()
    xticks = [0, 60, 120, 180, 240, 300, 359.9]
    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    xticklabels = ["0", "60E", "120E", "180", "120W", "60W", "0"]
    ax.set_xticklabels(xticklabels)
    ax.tick_params(axis='x', rotation=0)

    ax.set_ylim([-50,50])
    ax.set_yticks(np.linspace(-40, 40, 5), crs=ccrs.PlateCarree())
    ax.set_yticklabels([f"{int(x)}N" for x in np.linspace(-40, 40, 5)])

    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))

    ax.set_xlabel(r'Longitude ($^\circ$)')
    ax.set_ylabel(r'Latitude ($^\circ$)')


def get_TS_forecast_attributes(forecast):
    # get attributes from forecast file
    fc_init_date = pd.Timestamp(forecast.forecast_issue_date.values).strftime('%Y%m%d')
    forecast_period_start = pd.Timestamp(forecast.forecast_period_start.values).strftime('%Y%m%d')
    forecast_period_end = pd.Timestamp(forecast.forecast_period_end.values).strftime('%Y%m%d')
    teamname = forecast.teamname
    modelname = forecast.modelname

    fcwin = calc_fcwin(forecast)

    fig_title = f'Tercile probability of tropical storm days\nForecast details: Initialisation date: {fc_init_date}; forecast period: {forecast_period_start} to {forecast_period_end}\nTeamname: {teamname}; Modelname: {modelname}'

    sve_name = f'TS_{fc_init_date}_p{fcwin}_{teamname}_{modelname}.jpg'

    return fig_title, sve_name

def plot_basin_bars(ax, lon, lat, probs, cmap, norm):
    """
    lon, lat : basin position
    probs : length-3 array for tercile probabilities (0..1)
    cmap, norm : your forecast colormap + normalization
    """
    # Width and height of bars in map coords
    bar_width = 8      # degrees
    spacing = 15       # gap between bars

    # starting x-location (top bar)
    x0 = lon + bar_width
    basin_height_scale = 20.0

    for i, p in enumerate(probs):
        # bar color from colormap
        color = cmap(norm(p * 100.0))

        # rectangle definition
        rect = plt.Rectangle(
            (x0 + (bar_width+spacing)*i, lat),
            bar_width,
            p*basin_height_scale,
            color=color,
            ec='black',
            transform=ccrs.PlateCarree(),
            zorder=5,
        )
        ax.add_patch(rect)

        # white text inside
        label = f"{p*100:.1f}%"
        t=ax.text(
            x0 + (bar_width + spacing)*i + bar_width/2,
            lat - 2,     # place a bit below the baseline (lat)
            label,
            va='top',
            ha='center',
            color='black',
            fontsize=5.5,
            fontweight='bold',
            transform=ccrs.PlateCarree(),
            zorder=6
        )
        t.set_bbox(dict(boxstyle="round,pad=0.25",facecolor="white",edgecolor="black",linewidth=0.8,alpha=0.9))

def plot_basin_inactive_box(ax, lat_bounds, lon_bounds):
    """
    Plot a semi-transparent grey box with 'Inactive' label at basin location.

    lon, lat : basin reference position
    probs, cmap, norm : kept for compatibility but unused
    """
    lat_min, lat_max = lat_bounds
    lon_min, lon_max = lon_bounds

    # Case 1: no wrap (simple)
    if lon_min < lon_max:
        rect = plt.Rectangle(
            (lon_min, lat_min),
            lon_max - lon_min,
            lat_max - lat_min,
            fill=True,
            edgecolor='grey',
            fc='grey',
            transform=ccrs.PlateCarree(),
            zorder=4,alpha=0.4
        )
        ax.add_patch(rect)

    # Case 2: WRAPS the dateline → split into two boxes
    else:
        # Box 1: lon_min → 360
        rect1 = plt.Rectangle(
            (lon_min, lat_min),
            360 - lon_min,
            lat_max - lat_min,
            fill=True,
            edgecolor='grey',
            fc='grey',
            transform=ccrs.PlateCarree(),
            zorder=4,alpha=0.4
            )
        ax.add_patch(rect1)

        # Box 2: 0 → lon_max
        rect2 = plt.Rectangle(
            (0, lat_min),
            lon_max,
            lat_max - lat_min,
            fill=True,
            edgecolor='grey',
            fc='grey',
            transform=ccrs.PlateCarree(),
            zorder=4,alpha=0.4
        )
        ax.add_patch(rect2)

    lon_centre = ((lon_min + lon_max) / 2) % 360
    lat_centre = 0.5 * (lat_min + lat_max)

    ax.text(
        lon_centre,
        lat_centre,
        "Inactive",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
        transform=ccrs.PlateCarree(),
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor="black",
            alpha=0.85,
        ),
        zorder=5,
    )

def plot_basin_box(ax, lat_bounds, lon_bounds, edgecolor='red', linewidth=1.0):
    lat_min, lat_max = lat_bounds
    lon_min, lon_max = lon_bounds

    # Case 1: no wrap (simple)
    if lon_min < lon_max:
        rect = plt.Rectangle(
            (lon_min, lat_min),
            lon_max - lon_min,
            lat_max - lat_min,
            fill=False,
            edgecolor=edgecolor,
            linewidth=linewidth,
            transform=ccrs.PlateCarree(),
            zorder=4,
        )
        ax.add_patch(rect)

    # Case 2: WRAPS the dateline → split into two boxes
    else:
        # Box 1: lon_min → 360
        rect1 = plt.Rectangle(
            (lon_min, lat_min),
            360 - lon_min,
            lat_max - lat_min,
            fill=False,
            edgecolor=edgecolor,
            linewidth=linewidth,
            transform=ccrs.PlateCarree(),
            zorder=4,
        )
        ax.add_patch(rect1)

        # Box 2: 0 → lon_max
        rect2 = plt.Rectangle(
            (0, lat_min),
            lon_max,
            lat_max - lat_min,
            fill=False,
            edgecolor=edgecolor,
            linewidth=linewidth,
            transform=ccrs.PlateCarree(),
            zorder=4,
        )
        ax.add_patch(rect2)

def plot_TS_forecast(forecast,local_destination=None,format='jpg'):
    fig_title, sve_nme = get_TS_forecast_attributes(forecast)
    if local_destination:
        sve_nme = f'{local_destination}{sve_nme}'
    # assign format
    root, ext = os.path.splitext(sve_nme) # split the filename
    sve_nme = f"{root}.{format.lstrip('.')}" # take the root and add chosen format onto end

    basin_centers = {
    "ATL":   (265, 10),      # Atlantic
    "NWP":   (105, 20),      # Western North Pacific
    "SWIO":  (20, -25),      # Southwest Indian
    "SEIO":  (90, -25),     # Southeast Indian
     }

    # get month of forecasted period
    fc_lt_DAYS = (forecast.forecast_period_start - forecast.forecast_issue_date) / np.timedelta64(1, 'D')
    if fc_lt_DAYS > 18.0: # if week 4 lead time, subtract a week due to week 13 predictions!
        start_fc_day = forecast.forecast_period_start.values - np.timedelta64(7,'D')
    else:
        start_fc_day = forecast.forecast_period_start.values
    # if week 4 lead time, need to subtract a week
    fc_month = pd.Timestamp(start_fc_day).month

    fig, ax = plt.subplots(1,1,figsize=[6.4,3.5],gridspec_kw=dict(hspace=0.0),subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=180.0)))
    # generate colormap
    ai_wq_cmap, levels, norm = create_TS_colormap()
    # set formatting
    all_plot_choices_TS(ax)
    # plot forecast
    probs = forecast.values  # shape (3, 4)
    # Loop over each basin
    for j, basin in enumerate(forecast.basin.values):
        lat_bounds, lon_bounds = retrieve_training_data.get_basin_domain(basin,format360=True)
        lon, lat = basin_centers[basin]
        basin_probs = probs[:, j]
        if (fc_month in [6,7,8,9,10,11]) and (basin in ['ATL','NWP']):
            plot_basin_bars(ax, lon, lat, basin_probs, ai_wq_cmap, norm)
        elif (fc_month in [12,1,2]) and (basin in ['SWIO','SEIO']):
            plot_basin_bars(ax, lon, lat, basin_probs, ai_wq_cmap, norm)
        else:
            plot_basin_inactive_box(ax,lat_bounds,lon_bounds)
        # convert to 0 to 360.0
        print (basin)
        print (lon_bounds)
        #lon_bounds[0] = lon_bounds[0] if lon_bounds[0] >= 0 else lon_bounds[0] + 360
        #lon_bounds[1] = lon_bounds[1] if lon_bounds[1] >= 0 else lon_bounds[1] + 360
        plot_basin_box(ax, lat_bounds, lon_bounds)
    ax.set_title(fig_title,fontsize=10)
    fig.subplots_adjust(bottom=0.12)

    cbar_ax = fig.add_axes([0.05,0.13,0.9,0.02])
    CB = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=ai_wq_cmap),cax=cbar_ax,orientation='horizontal',pad=0.25,ticks=levels)
    CB.set_label('%')
    plt.savefig(sve_nme,dpi=200.0)
    plt.close()

