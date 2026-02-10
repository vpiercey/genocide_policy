
import pandas
import numpy as np

import load_fsi
import vis_tools_fsi
import load_tmk
import datasets

#

from sklearn import linear_model # for Lasso, etc.
from sklearn import metrics      # for, e.g., sklearn.metrics.roc_auc_score

############

# Suppress convergence warnings from sklearn; expect typically convergence 
# issues are related to extreme values of regularization parameters
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning
simplefilter("ignore", category=ConvergenceWarning)

############

'''
RESEARCH QUESTION:
    
    Given the FSI data from k years; year_{i}, year_{i-1}, ..., year_{i-k+1}, 
    predict the likelihood of an event at year_{i+L}.
    
    Training on **all known** events from all time; then bootstrapping 
    with sets of negatives of equal size.
    
    k : length of observation/memory
    L : forecast length (start with L=1).
    
    There are 12 indicators; so we are mapping 12k dimensions to 1 
    dimension (the binary prediction).
    
    Here, the question is how the ensemble of feature weightings varies depending 
    on the Elastic Net parameters used.
    
    ElasticNet follows the mixed objective:
        1 / (2 * n_samples) * ||y - Xw||^2_2
            + alpha * l1_ratio * ||w||_1
            + 0.5 * alpha * (1 - l1_ratio) * ||w||^2_2
    
    for which alpha (positive float) reflects degree of regularization to use; 
    l1_ratio (value on [0,1]) reflects the weighting toward 1-norm or 2-norm 
    regularization.
    
    TODO: isn't there a difference in units/scales in this objective function? 
        Shouldn't the 1-norm quantity be squared (or the 2-norm square rooted)? 
        Otherwise a re-scaling of units will interfere with regularization 
        parameters.
    
    See for details: 
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html
'''

k=1 # number of years of data prior to prediction 
L=1 # number of years out to forecast
X,y,meta = datasets.build_fsi_predicting_tmk(k=k, L=L, track_ongoing=False)

features=meta['features']

###############

# Build ensembles of models over a range of parameter space 
# (alpha, l1_ratio) in sklearn's ElasticNet to understand 
# dependence of conclusions about features with these.

import itertools

alphas = 2.0**np.arange(-10, 8) # 2**-10 (roughly 0.001) to 2**7 (128)
l1_ratios = 1/(1+2.0**np.arange(-7,8)) # values on (0,1); extremes at 0.008 and 0.992
l1_ratios = l1_ratios[::-1] # reverse order; smallest value first.

params = itertools.product(alphas, l1_ratios)

# TODO: each row will also have (country, year) pairs of data that went into 
# the construction of the model.

#
# misc
not_tmk_idx = np.where(y==0)[0]
yes_tmk_idx = np.where(y>0)[0]
num_tmk = len(yes_tmk_idx)

nboots = 10000

df_master = []

for _k, (_alpha, _l1_ratio) in enumerate(params):
    
    np.random.seed(10072023)
    
    models = []
    models_coef_ = np.zeros( (nboots, 12*k) )

    subsets = np.zeros((nboots, 2*num_tmk), dtype=int)
    trains = np.zeros((nboots, 2*num_tmk))
    tests = np.zeros((nboots, 2*num_tmk))
    aucrocs = np.zeros(nboots)

    for i in range(nboots):
        model = linear_model.ElasticNet(max_iter=1000, alpha=_alpha, l1_ratio=_l1_ratio, positive=False)
        
        negative_idx = np.random.choice(not_tmk_idx, num_tmk, replace=False)
        subset = np.concatenate( [yes_tmk_idx, negative_idx] )
        subsets[i] = subset
        
        model.fit(X[subset], y[subset])
        ypred = model.predict(X[subset])
        
        trains[i] = y[subset]
        tests[i] = ypred
        # can do more sophisticated things later...
        try:
            aucrocs[i] = metrics.roc_auc_score(y[subset], ypred)
        except:
            # TODO: think through.
            # probably doing regression instead of classification
            print('failed prediction with ', (_alpha, _l1_ratio, ))
            pass
        
        models.append(model)
        models_coef_[i] = model.coef_
        
    #
    
    df_results = pandas.DataFrame(data=models_coef_, columns=features )
    df_results['aucroc'] = aucrocs
    df_results['alpha'] = np.repeat(_alpha, nboots)
    df_results['l1_ratio'] = np.repeat(_l1_ratio, nboots)
    
    df_master.append( df_results )
    
    print(_k+1, 'of', len(alphas)*len(l1_ratios), ";", "alpha=%.4f"%_alpha, "l1_ratio=%.4f"%_l1_ratio)
    
    # build long dataframe solely for the purposes of visualization.
    #df_results = pandas.DataFrame(data=models_coef_,columns=features).melt(var_name='Indicator', value_name='Coefficient')
    #df_results['Indicator_group'] = [{'X':'S'}.get(v[0],v[0]) for v in df_results['Indicator']]

df_master = pandas.concat(df_master, ignore_index=True)

import datetime
tstamp = datetime.datetime.now().strftime('%Y-%b-%d-%H:%M')
df_master.to_csv( f'paramsweep_results_k={k}_L={L}_{tstamp}.csv', index=False)

