#import pandas
#import seaborn as sns
from matplotlib import pyplot as plt
import pandas
import numpy as np

import load_tmk
import datasets

#
from sklearn import metrics      # for, e.g., sklearn.metrics.roc_auc_score

######

plt.rcParams.update({'font.size': 16})
plt.style.use('ggplot')

########
'''
RESEARCH QUESTION:
    
    Given the *results* of k=1, L=1 prediction done in fsi_analysis5.py, 
    try to study geographic differences in predictive power.
    
'''


####

df_bootstrap_results = pandas.read_csv('bootstrap_pred_results_k1_L1.csv', index_col=None)

# this is MY (Manuch's) hand-created labeling.
# TODO: any kind of authoritative source on continent/region labeling.
df_country_labels = pandas.read_csv('countries_2023.csv')

# dictionary map of column "country" to column "region1"
# https://stackoverflow.com/a/71637532
_country_to_region = dict(zip(df_country_labels['country'], df_country_labels['region2']))

df_bootstrap_results['region2'] = df_bootstrap_results['country'].map(_country_to_region)


# Various ways to measure error/mismatched prediction
e = df_bootstrap_results['pred_prob'] - df_bootstrap_results['true_label']

df_bootstrap_results['score_err'] = e

df_bootstrap_results['quadratic_err'] = e*(1-e)

df_bootstrap_results['log_quadratic_err'] = np.sign(e)*np.log10( abs(e*(1-e)) )

#
import seaborn

# Acrobatics to structure plot as desired...
# https://seaborn.pydata.org/tutorial/axis_grids.html

g = seaborn.FacetGrid(data=df_bootstrap_results, col="region2", hue='region2', col_wrap=4, height=4, aspect=1)
g.map(seaborn.lineplot, "year", "score_err", estimator='median', errorbar=('pi', 50))

#seaborn.relplot(data=df_bootstrap_results, x='year', y='score_diff', col='region1', hue='region1', kind='line')

fig = plt.gcf()
ax = fig.get_axes()
for axi in ax:
    axi.axhline(0, color='#000', lw=1, linestyle='--')


fig.show()



