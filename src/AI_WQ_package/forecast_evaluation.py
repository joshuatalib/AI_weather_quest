# python script that contains functions for working out RPSS score
import numpy as np
import xarray as xr

def apply_land_sea_mask(score,land_sea_mask):
    # load in land sea mask
    score = score.where(land_sea_mask>=0.8)
    return score

def weighted_mean_calc(score):
    weights = np.cos(np.deg2rad(score.latitude))
    weights.name = 'weights'
    score_weighted = score.weighted(weights)
    # after weighting, extract selected lat region
    score_weighted_mean = score_weighted.mean(('latitude','longitude'))
    return score_weighted_mean

def conditional_obs_probs(obs,quintiles):
    num_quantiles=quintiles['quantile'].shape[0]

    threshold_crit = []

    for q in np.arange(num_quantiles+1):
        # if q == 0, check whether its lower than first quantile
        if q == 0:
            # need to transpose fc_data so ensemble member is first. 
            threshold_crit.append((obs < quintiles.values[0]))
        elif q == num_quantiles:
            # if at highest value, is it bigger than top quartile
            threshold_crit.append((obs > quintiles.values[-1]))
        else: # is it bigger or equal to previous quartile and smaller or equal to current quartile (i.e. 0.33 <= x <= 0.66).
            cond_1 = (quintiles.values[q-1] <= obs) # cond 1
            cond_2 = (obs <= quintiles.values[q])  # cond 2
            both_conds = xr.concat([cond_1,cond_2],dim='cond') # concat between both conditions 
            threshold_crit.append(both_conds.all(dim='cond')) # both conditions must be true

    all_crit = xr.concat(threshold_crit,dim='quintile')
    all_crit = all_crit.assign_coords({'quintile': ('quintile',np.arange(num_quantiles+1))})

    return all_crit

def work_out_RPSS(fc_pbs,obs_pbs,variable,land_sea_mask,quantile_dim='quintile'):
    # make both dataarray have same attribute sizes
    fc_pbs = fc_pbs.chunk({'quintile':5,'latitude':10,'longitude':10})
    obs_pbs = obs_pbs.chunk({'quintile':5,'latitude':10,'longitude':10})

    num_quants = fc_pbs.shape[0]

    # cumulate across quantiles
    fc_pbs_cumsum = fc_pbs.cumsum(dim=quantile_dim)
    obs_pbs_cumsum = obs_pbs.cumsum(dim=quantile_dim)
    # RPS score for forecast
    RPS_score_fc = ((fc_pbs_cumsum-obs_pbs_cumsum)**2.0).sum(dim=quantile_dim)

    # create an xarray filled with climatological probs (i.e. 0.2).
    clim_pbs = obs_pbs.where(False,1.0/num_quants) 
    clim_pbs_cumsum = clim_pbs.cumsum(dim=quantile_dim)
    RPS_score_clim = ((clim_pbs_cumsum-obs_pbs_cumsum)**2.0).sum(dim=quantile_dim)

    RPSS_wrt_clim = 1-(RPS_score_fc/RPS_score_clim)
    if variable == 't2m' or variable == 'pr':
        print ('applying land sea mask')
        RPSS_wrt_clim = apply_land_sea_mask(RPSS_wrt_clim,land_sea_mask)

    RPSS_wrt_clim_weighted = weighted_mean_calc(RPSS_wrt_clim)

    return RPSS_wrt_clim_weighted

