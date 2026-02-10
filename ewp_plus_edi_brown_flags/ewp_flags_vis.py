
import load_ewp_plus_flags as _duh
df = _duh.df

from sklearn import decomposition

from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap

import numpy as np

try:
    plt.style.use('tableau-colorblind10')
except:
    pass
plt.rcParams.update({'font.size': 16})
# Of particular interest are predicting any or all of the last 
# three labels:
#
# coercive_control
# existential_threat
# id_target_gps        (identified target groups)
#

X = df.iloc[:,3:-3]
X.drop('SFTGcode', axis=1, inplace=True)
y = df.iloc[:,-3:]

# drop categorical geographic region columns.
# drop outlier event (Libya 2022).
# TODO: follow up on how/why this event is an outlier.
if True:
    for col in ['reg.%s'%s for s in ['sca', 'eur', 'afr', 'eap', 'mna']]:
        X.drop(col, axis=1, inplace=True)

    # every single row has includesnonstate==1
    X.drop('includesnonstate', axis=1, inplace=True)
    
    #
    # Libya 2022
    X.drop(index=139, axis=0, inplace=True)
    y.drop(index=139, axis=0, inplace=True)
#

pca = decomposition.PCA()
#pca = decomposition.SparsePCA(n_components=2) # todo: percent variance explained with these vectors
#pca = decomposition.KernelPCA(n_components=2, kernel='rbf')


Xd = pca.fit_transform(X)
extent = [min(Xd[:,0]), max(Xd[:,0]), min(Xd[:,1]), max(Xd[:,1])]

fig,ax = plt.subplots(1,3, figsize=(13,4), sharex=True, sharey=True, constrained_layout=True)

for i in range(3):
    #ax[i].scatter(
    #    Xd[:,0], Xd[:,1], c=y.iloc[:,i], 
    #    label=df.columns[-3+i], cmap=plt.cm.cividis, edgecolors='k'
    #)
    
    # for each type of label,
    for _j,mask in [ (j, y.iloc[:,i]==j) for j in [0,1]]:
        # colormap based on increasing opacity of single color
        #basecolor = plt.cm.cividis(float(_j))
        basecolor = [(1,0,0,1), (0,0,1,1)][_j]
        colors = [(*basecolor[:3], z) for z in np.linspace(0,1,3)]
        
        mycm = LinearSegmentedColormap.from_list("moo", colors, N=8)
        # produce a hex histogram associated with the color.
        
        _temp = ax[i].hexbin(Xd[mask,0], Xd[mask,1], cmap=mycm, gridsize=10, mincnt=1,edgecolors='#666', linewidths=0.2, extent=extent, 
        vmin=0, vmax=20 # TODO: vmax algorithmically chosen.
        )
        # blank scatter to insert appropriate legends.
        ax[i].scatter([],[], c=[basecolor], label=['no', 'yes'][_j], marker='h', s=100)
        if i==2:
            eh = fig.colorbar(_temp)
            if _j==1:
                eh.set_ticklabels([])
    # 
    
    ax[i].set(xlabel='PC1')
    ax[i].xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax[i].yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax[i].set_title(df.columns[-3+i], loc='left', fontsize=18)
    ax[i].legend()

ax[0].set(ylabel='PC2')

######################

fig2,ax2 = plt.subplots(constrained_layout=True, figsize=(8,6))
ypos = np.arange(X.shape[1])
ypos = ypos[::-1]

ax2.barh(ypos, pca.components_[0], label='PC1 weights')
ax2.barh(ypos, pca.components_[1], label='PC2 weights')
ax2.grid()

ax2.xaxis.set_major_locator(ticker.MultipleLocator(0.5))

ax2.legend()
ax2.set(xlabel='Principal component weight', yticks=np.arange(X.shape[1]), yticklabels=X.columns)
################

fig.savefig('pca_ewp_hex_hist.pdf', bbox_inches='tight')
fig2.savefig('pca_ewp_pc_weights.pdf', bbox_inches='tight')

fig.savefig('pca_ewp_hex_hist.png', bbox_inches='tight')
fig2.savefig('pca_ewp_pc_weights.png', bbox_inches='tight')
#####################
fig.show()
fig2.show()

print('pct variance explained...')
print('pc1: ', pca.explained_variance_ratio_[0])
print('pc2: ', pca.explained_variance_ratio_[1])

