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
    
    Side-issue: if an event is happening or has happened, 
    data becomes biased/polluted/otherwise affected which may 
    affect downstream results.
'''

# Targeted Mass Killings data since 2006
k=2
L=1
X,y,meta = datasets.build_fsi_predicting_tmk(k=k,L=L)

features=meta['features']



# final labeled data set (!!)

###############

# naive fit produces a null model with Lasso.
# handle the imbalanced classes by 
# repeated training of all TMK cases (59 of them?)
# versus an 59 uniform iid selected non-TMK.

not_tmk_idx = np.where(y!=1)[0]
yes_tmk_idx = np.where(y==1)[0]
ntmk = len(yes_tmk_idx)

np.random.seed(10072023)
nboots = 10000
models = []
models_coef_ = np.zeros( (nboots, 12*k) )

subsets = np.zeros((nboots, 2*ntmk), dtype=int)
trains = np.zeros((nboots, 2*ntmk))
tests = np.zeros((nboots, 2*ntmk))
aucrocs = np.zeros(nboots)

for i in range(nboots):
    model = linear_model.ElasticNet(max_iter=1e4, l1_ratio=0.05, positive=False) # idk lol
    
    subset = np.concatenate( [yes_tmk_idx, np.random.choice(not_tmk_idx, ntmk, replace=False)] )
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
        pass
    
    models.append(model)
    models_coef_[i] = model.coef_
    
    #print(i, '%.3f'%aucrocs[i])
#

# build long dataframe solely for the purposes of visualization.
df_results = pandas.DataFrame(data=models_coef_,columns=features).melt(var_name='Indicator', value_name='Coefficient')
df_results['Indicator_group'] = [{'X':'S'}.get(v[0],v[0]) for v in df_results['Indicator']]

#
if True:
    fig,ax = plt.subplots(figsize=(12,8), constrained_layout=True)
    seaborn.barplot(data=df_results, y='Indicator', x='Coefficient', 
                    alpha=0.5, hue='Indicator_group', palette='tab10', 
                    estimator=np.median, errorbar=lambda v: np.quantile(v,[0.1,0.9]), 
                    dodge=False, capsize=0.5, width=0.95)
    
    # figure polish
    ax.set_xlim(-max(np.abs(ax.get_xlim())), max(np.abs(ax.get_xlim())))
    ax.axvline(0,c='k', lw=3)
    ax.set_title('FSI indicator feature importance (predicting TMK year%i)'%(k+L-1), loc='left', fontsize=24)
    seaborn.move_legend(ax, loc='upper left')
    
    fig.savefig('FSI_predicting_TMK_k%i_L%i.png'%(k,L), bbox_inches='tight')
