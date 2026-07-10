# SPDX-FileCopyrightText: 2024 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

# python script that contains functions for working out RPSS score
import numpy as np
import xarray as xr

def apply_region_mask(score,nlat,slat,wlon,elon):
    if wlon < elon:
        region_mask = (
                      (score.latitude >= slat) &
                      (score.latitude <= nlat) &
                      (score.longitude >= wlon) &
                      (score.longitude <= elon)
                      )
    else:
        # wrapped case, i.e. w=335 and e=60
        region_mask = (
                      (score.latitude >= slat) &
                      (score.latitude <= nlat) &
                      (
                      (score.longitude >= wlon) | # OR instead of an AND
                      (score.longitude <= elon)
                      )
                      )

    score_masked = score.where(region_mask)

    return score_masked

def apply_land_sea_mask(score,land_sea_mask,quintile_dim=None):
    if quintile_dim:
        land_sea_mask = land_sea_mask.expand_dims(quintile=score.coords["quintile"])
    # load in land sea mask
    score = score.where(land_sea_mask>=0.5)
    return score

def apply_lat_weighting(score):
    weights_1d = np.cos(np.deg2rad(score.latitude))
    weights_1d.name = 'weights'

    # broadcast to match 2D grid
    weights_2d = weights_1d.broadcast_like(score)
    weights_2d = weights_2d/weights_2d.mean() # added on 30th Oct 2025 to standardise weights

    # apply weights
    score_weighted = score*weights_2d
    return score_weighted

def calculate_global_mean(score):
    score_mean = score.mean(('latitude','longitude'),skipna=True)
    return score_mean

def conditional_obs_probs(obs,quintile_bounds):
    # allowing multiple quantile names due to terciles for TSs
    valid_names = {"tercile", "quintile", "quantile"}

    quantile_name = quintile_bounds.dims[0]

    if quantile_name not in valid_names:
        raise ValueError(
            f"Expected dimension one of {valid_names}, got '{quantile_name}'"
        )

    num_quantiles=quintile_bounds[quantile_name].shape[0]

    threshold_crit = []

    for q in np.arange(num_quantiles+1):
        # if q == 0, check whether its lower than first quantile
        if q == 0:
            # need to transpose fc_data so ensemble member is first. 
            threshold_crit.append((obs < quintile_bounds.values[0]))
        elif q == num_quantiles:
            # if at highest value, is it bigger or equal to top quartile
            threshold_crit.append((obs >= quintile_bounds.values[-1]))
        else: # is it bigger or equal to previous quartile and smaller or equal to current quartile (i.e. 0.33 <= x <= 0.66).
            # 2nd Apr '25 - bug fixed in light of quintiles possibly having same value (i.e. 0 mm for quintile 0.2 and 0.4).
            lower_bound = quintile_bounds.values[q-1]
            upper_bound = quintile_bounds.values[q]

            in_range = (lower_bound <= obs) & (obs < upper_bound) # is the observation within the two bounds

            # check that lower bound is not the same as higher bound. If it is, do not count as within quintile bound.
            bound_neq = (lower_bound != upper_bound)

            # check both
            in_range_highest_bound = in_range & bound_neq

            threshold_crit.append(in_range_highest_bound)# both conditions must be true

    all_crit = xr.concat(threshold_crit,dim=quantile_name)
    all_crit = all_crit.assign_coords({quantile_name: (quantile_name,np.arange(num_quantiles+1))})

    # 28th July 2025 change - when all quintiles equal the same value, i.e. 0 mm precipitation for all five quintiles, i.e. desert, mask out values with np.nan
    all_equal = (quintile_bounds.min(dim=quantile_name) == quintile_bounds.max(dim=quantile_name))
    all_crit = all_crit.where(~all_equal)

    return all_crit

def calculate_RPS(fc_pbs,obs_pbs,variable,land_sea_mask,lat_weighting=True,global_mean=True):
    fc_q_name = get_quantile_dimname(fc_pbs)
    obs_q_name = get_quantile_dimname(obs_pbs)
    
    # cumulate across quantiles
    fc_pbs_cumsum = fc_pbs.cumsum(dim=fc_q_name)
    obs_pbs_cumsum = obs_pbs.cumsum(dim=obs_q_name)
    
    # RPS score for forecast
    # work out squared value of cumulative difference
    cum_pbs_diff = fc_pbs_cumsum.copy()
    cum_pbs_diff.values = ((fc_pbs_cumsum.values-obs_pbs_cumsum.values)**2.0) # square the cumulative difference between forecast prob and obs prob. Call the actual data within the xarray.
    RPS_score = cum_pbs_diff.sum(dim=fc_q_name,skipna=True)

    # 28th July 2025 edit. mask where nan_quintile mask= True, i.e. where in obs_pbs, zero rainfall
    # create mask where obs_pbs == np.nan (i.e. in deserts, set in conditional obs probs function). only np.nans will exist in precip.
    nan_quintile_mask = obs_pbs.isnull().all(dim=obs_q_name)
    RPS_score = RPS_score.where(~nan_quintile_mask)

    # apply a land sea mask
    if variable == 'tas' or variable == 'pr':
        print ('applying land sea mask')
        RPS_score = apply_land_sea_mask(RPS_score,land_sea_mask)

    # work out weighted average
    if lat_weighting:
        RPS_score = apply_lat_weighting(RPS_score) # applies a weighting to the RPS so each point is considered based on area (i.e. greater weighting to equatorial grid points)
    if global_mean:
        RPS_score = calculate_global_mean(RPS_score) # average across latitude and longitude

    print (RPS_score.values)
    return RPS_score

def get_quantile_dimname(da):
    # make both dataarray have same attribute sizes
    if "quintile" in da.dims:
        qdim = "quintile"
    elif "quantile" in da.dims:
        qdim = "quantile"
    elif "tercile" in da.dims:
        qdim = "tercile"
    else:
        raise ValueError(
            f"Could not find quintile/quantile dimension. "
            f"Available dimensions: {da.dims}"
        )
    return qdim

def work_out_RPSS(fc_pbs,obs_pbs,variable,land_sea_mask):
    # find quintile name
    fc_q_name = get_quantile_dimname(fc_pbs)
    obs_q_name = get_quantile_dimname(obs_pbs)

    # make both dataarray have same attribute sizes
    fc_pbs = fc_pbs.chunk({fc_q_name:5,'latitude':10,'longitude':10})
    obs_pbs = obs_pbs.chunk({obs_q_name:5,'latitude':10,'longitude':10})

    num_quants = fc_pbs.shape[0]

    # RPS score for forecast
    print ('RPS for submitted forecast')
    RPS_score_fc = calculate_RPS(fc_pbs,obs_pbs,variable,land_sea_mask)

    # create an xarray filled with climatological probs (i.e. 0.2).
    clim_pbs = obs_pbs.where(False,1.0/num_quants)
    print ('RPS for climatology')
    RPS_score_clim = calculate_RPS(clim_pbs,obs_pbs,variable,land_sea_mask)

    print ('RPSS with respect to climatology')
    RPSS_wrt_clim = 1-(RPS_score_fc/RPS_score_clim)
    print (RPSS_wrt_clim.values)
    
    return RPSS_wrt_clim

def calculate_RPS_TS(fc_pbs,obs_pbs):
    # find quantile name
    fc_q_name = get_quantile_dimname(fc_pbs)
    obs_q_name = get_quantile_dimname(obs_pbs)

    # cumulate across quantiles
    fc_pbs_cumsum = fc_pbs.cumsum(dim=fc_q_name)
    obs_pbs_cumsum = obs_pbs.cumsum(dim=obs_q_name)

    # RPS score for forecast
    # work out squared value of cumulative difference
    cum_pbs_diff = fc_pbs_cumsum.copy()
    cum_pbs_diff.values = ((fc_pbs_cumsum.values-obs_pbs_cumsum.values)**2.0) # square the cumulative difference between forecast prob and obs prob. Call the actual data within the xarray.
    RPS_score = cum_pbs_diff.sum(dim=fc_q_name,skipna=True)

    nan_quantile_mask = obs_pbs.isnull().all(dim=obs_q_name)
    RPS_score = RPS_score.where(~nan_quantile_mask)

    return RPS_score

def calculate_RPSS_TS(fc_pbs,obs_pbs):
    num_quants = fc_pbs.shape[0]

    # RPS score for forecast
    print ('RPS for submitted forecast')
    RPS_score_fc = calculate_RPS_TS(fc_pbs,obs_pbs)

    # create an xarray filled with climatological probs (i.e. 0.2).
    clim_pbs = obs_pbs.where(False,1.0/num_quants)
    print ('RPS for climatology')
    RPS_score_clim = calculate_RPS_TS(clim_pbs,obs_pbs)

    print ('RPSS with respect to climatology')
    RPSS_wrt_clim = 1-(RPS_score_fc/RPS_score_clim)
    print (RPSS_wrt_clim.values)

    return RPSS_wrt_clim

def calculate_MJO_brier_score(fc_pbs,obs_pbs):
    return ((fc_pbs-obs_pbs)**2.0).mean('MJO_phase')


