#import pandas
#import seaborn as sns
from matplotlib import pyplot as plt
import pandas
import numpy as np

import load_fsi
import vis_tools_fsi
import load_tmk
import datasets

#

from sklearn import linear_model # for Lasso, etc.
from sklearn import metrics      # for, e.g., sklearn.metrics.roc_auc_score

#

import seaborn

######

plt.rcParams.update({'font.size': 16})
plt.style.use('seaborn-whitegrid')

########
'''
RESEARCH QUESTION:
    
    Given the FSI data from k years; year_{i}, year_{i-1}, ..., year_{i-k+1}, 
    predict the likelihood of an event at year_{i+L}.
    
    k : length of observation/memory
    L : forecast length (start with L=1).
    
    There are 12 indicators; so we are mapping 12k dimensions to 1 
    dimension. 
    
    In adjustment to analysis3: I would like to add two 
    nuances to investigate the prediction problem:
        1. Select only TMK events after a period of peace (k years), 
           chronologically, for a given country; the rest must be thrown out.
           (expecting fewer positive examples)
        2. Do some type of train/test methodology, 
           even with this methodology.
        3. (For the future): compare countries' data points
           restricted to a given year. For example, 
           build a classifier based on data year 2010.
'''

# Targeted Mass Killings data since 2006
k=1
L=1
X,y,meta = datasets.build_fsi_predicting_tmk(k=k, L=L, track_ongoing=False)

features=meta['features']
countries_flat = np.concatenate(meta['countries'])
years_flat = np.concatenate(meta['years'])


# final labeled data set (!!)

###############

'''
Proper train/test scheme now proceeds as follows:
    
    select ntmk samples from each class.
    subdivide into training testing sets; ns from each class in training.
    Train; then evaluate and store probabilities for later evaluation of results.

    Last issue: this naive approach breaks causality (future events may be 
    in the training set to predict past events)
'''

ns = 15

not_tmk_idx = np.where(y==0)[0]
yes_tmk_idx = np.where(y>0)[0]
ntmk = len(yes_tmk_idx)
print("k: %i, L: %i, ntmk: %i"%(k,L,ntmk) )

np.random.seed(10072023)
nboots = 10000
models = []
models_coef_ = np.zeros( (nboots, 12*k) )

subsets = np.zeros((nboots, 2*ntmk), dtype=int)
trains = np.zeros((nboots, 2*ns))
tests = np.zeros((nboots, 2*(ntmk-ns)))
preds = np.zeros((nboots, 2*(ntmk-ns)))
aucrocs = np.zeros(nboots)

train_idxs = np.zeros((nboots, 2*ns), dtype=int)
test_idxs = np.zeros((nboots, 2*(ntmk-ns)), dtype=int)

for i in range(nboots):
    #model = linear_model.ElasticNet(max_iter=1e4, l1_ratio=0.05, positive=False) # idk lol
    model = linear_model.LogisticRegression(max_iter=1e4, penalty='elasticnet', solver='saga', l1_ratio=0.05)
    
    not_tmk_idx_choice = np.random.choice(not_tmk_idx, ntmk, replace=False)
    subset = np.concatenate( [yes_tmk_idx, not_tmk_idx_choice] )
    
    subsets[i] = subset
    
    train_idx = np.concatenate([np.random.choice(yes_tmk_idx, ns, replace=False), np.random.choice(not_tmk_idx_choice, ns, replace=False)])
    test_idx = np.setdiff1d(subset, train_idx)
    
    train_idxs[i] = train_idx
    test_idxs[i] = test_idx
    
    model.fit(X[train_idx], y[train_idx])
    ypred = model.predict_proba(X[test_idx])[:,1]
    
    trains[i] = y[train_idx]
    tests[i] = y[test_idx]
    preds[i] = ypred
    # can do more sophisticated things later...

    aucrocs[i] = metrics.roc_auc_score(tests[i], preds[i])
    
    models.append(model)
    models_coef_[i] = model.coef_
    
    #print(i, '%.3f'%aucrocs[i])
#

# build long dataframe solely for the purposes of visualization.
df_results = pandas.DataFrame(data=models_coef_,columns=features).melt(var_name='Indicator', value_name='Coefficient')
df_results['Indicator_group'] = [{'X':'S'}.get(v[0],v[0]) for v in df_results['Indicator']]


############
# build dataframe to export results.

# table 1...
# country, year, tmk label, predicted probability, bootstrap number
columns = ['country', 'year', 'true_label', 'pred_prob', 'bootstrap_number']
_cc = countries_flat[ test_idxs ].flatten()
_yy = years_flat[ test_idxs ].flatten()
_cy = [(_cc[i], _yy[i]) for i in range(len(_cc))]
_tt = tests.flatten()
_pp = preds.flatten()
_bb = np.repeat(np.arange(nboots), 2*(ntmk-ns))

df_crossval = pandas.DataFrame({header: dat for (header,dat) in zip(columns, [_cc, _yy, _tt, _pp, _bb])})


# table 2...
# bootstrap number, (country1, year1), (country2, year2), ..., (countryM, yearM) in training data.



############

#
if True:
    all_curves = [metrics.roc_curve(tests[i],preds[i], drop_intermediate=False) for i in range(nboots)]
    all_curves = np.array(all_curves)
    # plot performance measured by AUC ROC
    fig,ax = plt.subplots(1,2, figsize=(12,6), constrained_layout=True)
    
    # plot an arbitrary subset of ROC curves
    #for i in range(0, nboots, int(nboots/10000)):
    #    ax[0].plot(all_curves[i][0], all_curves[i][1], c='#666', alpha=0.1, lw=4)
    ax[0].plot(all_curves[0,0,:], all_curves[:,1,:].T, c='#666', alpha=0.1, lw=4)
    ax[1].hist(aucrocs, bins=np.linspace(0,1,41), edgecolor='k', linewidth=0.5)
    
    ax[0].set(xlim=(0,1), ylim=(0,1), xlabel="FPR", ylabel="TPR")
    ax[1].set(xlim=(0,1), xlabel="AUCROC", ylabel="Count")
    
    fig.savefig("bootstrap_traintest_pred_k%i_L%i.png"%(k,L), bbox_inches='tight')
    fig.savefig("bootstrap_traintest_pred_k%i_L%i.pdf"%(k,L), bbox_inches='tight')
    
    df_crossval.to_csv("bootstrap_pred_results_k%i_L%i.csv"%(k,L), index=False)
    