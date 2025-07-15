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

    # apply weights
    score_weighted = score*weights_2d
    return score_weighted

def calculate_global_mean(score):
    score_mean = score.mean(('latitude','longitude'),skipna=True)
    return score_mean

#def weighted_mean_calc(score,weighted_only=False):
#    weights = np.cos(np.deg2rad(score.latitude))
#    weights.name = 'weights'
#    # apply weights
#    score_weighted = score.weighted(weights)
#   if weighted_only:
#        weights_2d = weights.broadcast_like(score)
#        score_weighted = score*weights_2d
#        return score_weighted
#    else:
#        # after weighting, extract selected lat region
#        score_weighted_mean = score_weighted.mean(('latitude','longitude'))
#       return score_weighted_mean

def conditional_obs_probs(obs,quintile_bounds):
    num_quantiles=quintile_bounds['quantile'].shape[0]

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

    all_crit = xr.concat(threshold_crit,dim='quintile')
    all_crit = all_crit.assign_coords({'quintile': ('quintile',np.arange(num_quantiles+1))})

    return all_crit

def calculate_RPS(fc_pbs,obs_pbs,variable,land_sea_mask,quantile_dim='quintile',lat_weighting=True,global_mean=True):
    # cumulate across quantiles
    fc_pbs_cumsum = fc_pbs.cumsum(dim=quantile_dim)
    obs_pbs_cumsum = obs_pbs.cumsum(dim=quantile_dim)
    
    # RPS score for forecast
    # work out squared value of cumulative difference
    cum_pbs_diff = fc_pbs_cumsum.copy()
    cum_pbs_diff.values = ((fc_pbs_cumsum.values-obs_pbs_cumsum.values)**2.0) # square the cumulative difference between forecast prob and obs prob. Call the actual data within the xarray.
    print (cum_pbs_diff.mean().values)
    RPS_score = cum_pbs_diff.sum(dim=quantile_dim,skipna=True)

    # apply a land sea mask
    if variable == 'tas' or variable == 'pr':
        print ('applying land sea mask')
        RPS_score = apply_land_sea_mask(RPS_score,land_sea_mask)

    # work out weighted average
    if lat_weighting:
        RPS_score = apply_lat_weighting(RPS_score) # applies a weighting to the RPS so each point is considered based on area (i.e. greater weighting to equatorial grid points)
    if global_mean:
        RPS_score = calculate_global_mean(RPS_score) # average across latitude and longitude

    return RPS_score

def work_out_RPSS(fc_pbs,obs_pbs,variable,land_sea_mask,quantile_dim='quintile'):
    # make both dataarray have same attribute sizes
    fc_pbs = fc_pbs.chunk({'quintile':5,'latitude':10,'longitude':10})
    obs_pbs = obs_pbs.chunk({'quintile':5,'latitude':10,'longitude':10})

    num_quants = fc_pbs.shape[0]

    # RPS score for forecast
    RPS_score_fc = calculate_RPS(fc_pbs,obs_pbs,variable,land_sea_mask)

    # create an xarray filled with climatological probs (i.e. 0.2).
    clim_pbs = obs_pbs.where(False,1.0/num_quants) 
    RPS_score_clim = calculate_RPS(clim_pbs,obs_pbs,variable,land_sea_mask)

    RPSS_wrt_clim = 1-(RPS_score_fc/RPS_score_clim)

    return RPSS_wrt_clim
