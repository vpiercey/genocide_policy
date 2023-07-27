'''

Goal: 
    Compare Early Warning project scores for each 
    country to those produced during our bootstrapping.
    
    There are various nuances in differences in 
    methodology, but the main interest is to answer 
    how consistent our scorings are with theirs, 
    for the easiest to handle data set (2022-2023)
'''

import pandas
import datasets
import numpy as np

import seaborn
from matplotlib import pyplot as plt


df_our = datasets.our_bootstrap_results_k1_L1()
df_ewp = datasets.ewp_2022_23_raw()

####
# cleanup

# Country renamings only to aid score comparison
df_ewp.replace({"Burma/Myanmar": "Myanmar"}, inplace=True)
df_ewp.sort_values('country', inplace=True)
df_ewp.set_index('country', inplace=True)

ewp_countries = df_ewp.index.unique()

# TODO: strictly necessary?
ewp_mask = df_our['country'].isin(ewp_countries)
df_our = df_our[ewp_mask]

#####
# numerical score dict

# For analysis, insert columns in *our* data set 
# where EWP scores get mapped via dictionary.

for ewp_col in ['risk_in_2022', 'risk_in_2022_23']:
    mappable = df_ewp[ewp_col].to_dict()
    df_our['ewp_'+ewp_col] = df_our['country'].map(mappable)
    
####
# visualization
plt.style.use('seaborn-whitegrid')
plt.rcParams.update({'font.size': 18})
fig,ax = plt.subplots(figsize=(10,8), constrained_layout=True)

#
target_year = 2022
target_ewp_col = 'ewp_risk_in_2022'
df_compare = df_our[ df_our['year']==target_year ]

#ax.scatter(df_compare['pred_prob'], df_compare['ewp_risk_in_2022_23'], s=10, alpha=0.4)
my_cm = plt.cm.magma_r.copy()
my_cm.set_under([0,0,0,0])
my_cm.set_bad([0,0,0,0])
plot_obj = ax.hexbin(df_compare['pred_prob'], df_compare[target_ewp_col], gridsize=20, bins='log', cmap=my_cm, vmin=2)
ax.set(xlabel='Risk; FSI + TMK + LR', ylabel='Risk; EWP')

fig.colorbar(plot_obj, label='Count')
fig.savefig('ewp_vs_fsi_v1_%i.png'%target_year, bbox_inches='tight')
fig.savefig('ewp_vs_fsi_v1_%i.pdf'%target_year, bbox_inches='tight')
