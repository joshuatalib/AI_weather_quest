# python script that contains functions for working out RPSS score
import numpy as np
import xarray as xr

def apply_land_sea_mask(score,land_sea_mask):
    lsm_expanded = land_sea_mask.expand_dims(dim={"quintile":score.quintile},axis=0)
    # load in land sea mask
    score = score.where(lsm_expanded>=0.8)
    return score

def weighted_mean_calc(score,weighted_only=False):
    weights = np.cos(np.deg2rad(score.latitude))
    weights.name = 'weights'
    # applky weights
    score_weighted = score.weighted(weights)
    if weighted_only:
        weights_2d = weights.broadcast_like(score)
        score_weighted = score*weights_2d
        return score_weighted
    else:
        # after weighting, extract selected lat region
        score_weighted_mean = score_weighted.mean(('latitude','longitude'))
        return score_weighted_mean

def conditional_obs_probs(obs,quintile_bounds):
    num_quantiles=quintile_bounds['quantile'].shape[0]

    threshold_crit = []

    for q in np.arange(num_quantiles+1):
        # if q == 0, check whether its lower than first quantile
        if q == 0:
            # need to transpose fc_data so ensemble member is first. 
            threshold_crit.append((obs < quintile_bounds.values[0]))
        elif q == num_quantiles:
            # if at highest value, is it bigger than top quartile
            threshold_crit.append((obs > quintile_bounds.values[-1]))
        else: # is it bigger or equal to previous quartile and smaller or equal to current quartile (i.e. 0.33 <= x <= 0.66).
            cond_1 = (quintile_bounds.values[q-1] <= obs) # cond 1
            cond_2 = (obs <= quintile_bounds.values[q])  # cond 2
            both_conds = xr.concat([cond_1,cond_2],dim='cond') # concat between both conditions 
            threshold_crit.append(both_conds.all(dim='cond')) # both conditions must be true

    all_crit = xr.concat(threshold_crit,dim='quintile')
    all_crit = all_crit.assign_coords({'quintile': ('quintile',np.arange(num_quantiles+1))})

    return all_crit

def calculate_RPS(fc_pbs,obs_pbs,variable,land_sea_mask,quantile_dim='quintile',weighted_only=False):
    # cumulate across quantiles
    fc_pbs_cumsum = fc_pbs.cumsum(dim=quantile_dim)
    obs_pbs_cumsum = obs_pbs.cumsum(dim=quantile_dim)
    # apply a land sea mask
    if variable == 't2m' or variable == 'pr':
        print ('applying land sea mask')
        fc_pbs_cumsum = apply_land_sea_mask(fc_pbs_cumsum,land_sea_mask)
        obs_pbs_cumsum = apply_land_sea_mask(obs_pbs_cumsum,land_sea_mask)
    
    # RPS score for forecast
    RPS_score = ((fc_pbs_cumsum-obs_pbs_cumsum)**2.0).sum(dim=quantile_dim)

    # work out weighted average
    if weighted_only:
        RPS_score = weighted_mean_calc(RPS_score,weighted_only=True)
    else:
        RPS_score = weighted_mean_calc(RPS_score)

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

