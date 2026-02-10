'''
Analysis of features as result of output of 
fsi_analysis_feature_robustness.py
'''

import pandas
from matplotlib import pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 14})

# unimportant: i like this colormap better.
# as long as it's not plt.cm.magma we're good.
try:
    import cmocean
    count_cm = cmocean.cm.deep_r
except:
    count_cm = plt.cm.viridis
#


#df = pandas.read_csv('paramsweep_results_k=2_L=1_2024-Jun-24-04:43.csv')
df = pandas.read_csv('paramsweep_results_k=1_L=1_2024-Jun-24-08:11.csv')


# Question: when do we see features agreeing?
synthesis = []
nfeat_threshold = 1000

nfeat = df.shape[1] - 3

for (_a,_l),dfs in df.groupby(['alpha', 'l1_ratio']):
    feats = dfs.iloc[:,:nfeat]
    sig = (feats.abs() > 0.05).sum()
    #break

    synthesis.append([
        _a,_l,
        *np.quantile(dfs['aucroc'], q=[0.1,0.5,0.9]),
        *list(sig)
    ])
#

df_feat_sel = pandas.DataFrame(synthesis, columns=['alpha', 'l1_ratio', 'aucroc0.1', 'aucroc0.5', 'aucroc0.9', *df.columns[:nfeat]])

df_feat_sel_succ = df_feat_sel[df_feat_sel['aucroc0.5'] > 0.9]

# overall, count how many times features are present in the top n.
print( df_feat_sel.melt(value_vars=df.columns[:nfeat]).value_counts('value') )
print('num rows: ', df_feat_sel.shape[0])

print('==========')
# ignoring parameter pairs that had significant failures to predict training 
# data (aucroc0.1), does the picture change?

#print( df_feat_sel_succ.melt(value_vars=df.columns[:12*2]).value_counts('value') )
print('num rows: ', df_feat_sel_succ.shape[0])


###########
fig,ax = plt.subplots(constrained_layout=True, figsize=(8,6))
# plot contours of AUCROC to get a sense of what parameter combinations 
# succeed in fitting the training data, at least.
con = ax.tricontourf(df['alpha'], df['l1_ratio'], df['aucroc'], vmin=0.5, vmax=1, levels=np.linspace(0.5,1,11), cmap=plt.cm.magma)
fig.colorbar(con, label='AUCROC')
#con2 = ax.tricontour(df['alpha'], df['l1_ratio'], df['aucroc'], vmin=0.5, vmax=1, levels=6, linewidths=2, cmap=plt.cm.magma)
#ax.clabel(con2, con2.levels, inline=True, fmt='%.1f', fontsize=14)

# polishing
ax.set(xscale='log', 
xlabel=r"$\alpha (regularization)$", 
ylabel=r"$l_1$ ratio"
)
ax.set_title('Elastic Net training AUC parameter dependence', loc='left')

for _v in df['alpha'].unique():
    ax.axvline(_v, c='#666', lw=0.3)
for _v in df['l1_ratio'].unique():
    ax.axhline(_v, c='#666', lw=0.3)


fig.savefig('fsi_tmk_elasticnet_train_aucroc_performance.png')

#######################################
#
##
# PART 2: Picking the three indicators identified from initial analysis,
# what level of frequency do they appear in parameter space over 
# 10000 bootstrap samples? 
# 
fig2,ax2 = plt.subplots(1,3, constrained_layout=True, figsize=(13,4))


count_upper = 8000
levels = 9
for _j,indicator in enumerate(['C1_Y0', 'C3_Y0', 'S2_Y0']):
    con = ax2[_j].tricontourf(
        df_feat_sel_succ['alpha'], 
        df_feat_sel_succ['l1_ratio'], 
        df_feat_sel_succ[indicator], 
        vmin=0, vmax=count_upper, levels=np.linspace(0, count_upper, 11), 
        cmap=count_cm
        )
    
    # polishing
    ax2[_j].set(xscale='log', xlabel=r"$\alpha (regularization)$")
    ax2[_j].set_title(indicator, loc='left')
    for _v in df['alpha'].unique():
        ax2[_j].axvline(_v, c='#666', lw=0.3)
    for _v in df['l1_ratio'].unique():
        ax2[_j].axhline(_v, c='#666', lw=0.3)

#

# polishing
ax2[0].set(ylabel=r"$l_1$ ratio")


fig2.colorbar(con, label='Count')
fig2.show()

fig2.savefig('feature_sel_counts1.png', bbox_inches='tight')

###################################

# Part 3: same as part 2, but looking at P1 and P3 which are showing up more.
fig3,ax3 = plt.subplots(1,2, constrained_layout=True, figsize=(9,4))

count_upper = 8000
levels = 9
for _j,indicator in enumerate(['P1_Y0', 'P3_Y0']):
    con = ax3[_j].tricontourf(
        df_feat_sel_succ['alpha'], 
        df_feat_sel_succ['l1_ratio'], 
        df_feat_sel_succ[indicator], 
        vmin=0, vmax=count_upper, levels=np.linspace(0, count_upper, 11), 
        cmap=count_cm
        )
    
    # polishing
    ax3[_j].set(xscale='log', xlabel=r"$\alpha (regularization)$")
    ax3[_j].set_title(indicator, loc='left')
    for _v in df['alpha'].unique():
        ax3[_j].axvline(_v, c='#666', lw=0.3)
    for _v in df['l1_ratio'].unique():
        ax3[_j].axhline(_v, c='#666', lw=0.3)

#

# polishing
ax3[0].set(ylabel=r"$l_1$ ratio")

fig3.colorbar(con, label='Count')
fig3.show()

fig3.savefig('feature_sel_counts2.png', bbox_inches='tight')


