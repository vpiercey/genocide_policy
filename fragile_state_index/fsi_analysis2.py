#import pandas
#import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np

import load_fsi
import vis_tools_fsi
import load_tmk

plt.rcParams.update({'font.size': 14})
plt.style.use('seaborn-whitegrid')

##

# Targeted Mass Killings data since 2006
df_tmk = load_tmk.load()
df_tmk = df_tmk[ df_tmk['year'] >= 2006 ]

tmk_actors = df_tmk['country'].str.split(', ')
tmk_actors_unique = np.unique( np.concatenate(tmk_actors.values) )

# Fragile State Index 
df_fsi = load_fsi.load_joined()
load_fsi.shorten_indicators(df_fsi)

df_fsi = load_fsi.to_long(df_fsi)

# This is ad-hoc since there are fewer than 16 unique
# countries in the TMK database after 2006.
fig,ax = plt.subplots(
    4,5, figsize=(15,12), sharex=True, sharey=True, 
    constrained_layout=True
    )

# TODO: map country names to FSI names to build plots automatically.
reassign_country = {
    'DR Congo (Zaire)': 'Congo Democratic Republic',
    'Ivory Coast': "Cote d'Ivoire",
    'Myanmar (Burma)': "Myanmar"
}

k=0
c2ax={}
for i in range(ax.shape[0]):
    for j in range(ax.shape[1]):
        if k==len(tmk_actors_unique):
            break
        try:
            # replace the country name if I've manually coded it in.
            country = reassign_country.get(tmk_actors_unique[k], tmk_actors_unique[k])
            
            # fetch data
            vis_tools_fsi.profile_country_brief(df_fsi, country, ax[i,j])
            
            # store a map of country names to subplot for later use.
            c2ax[tmk_actors_unique[k]] = ax[i,j]
        except:
            pass
        _leg = ax[i,j].get_legend()
        if _leg is not None: #and (i>0 or j>0): # TODO: place the legend somewhere.
            _leg.remove()
        k+=1
#
for z in range(k,np.prod(ax.shape)):
    i,j = int(z/ax.shape[1]), z%ax.shape[1]
    ax[i,j].remove()

# For each TMK, identify the countries, then plot a region on the 
# associated plot.
covered = {}
for event in df_tmk.iloc:
    involved_parties = event['country'].split(', ')
    for country in involved_parties:
        _ax = c2ax.get(country, None)
        if _ax is None:
            continue
        
        if country not in covered:
            covered[country] = []
        if event['year'] in covered[country]:
            continue
        _ax.axvspan(event['year'], event['year']+1, facecolor='#ccb', edgecolor='#ffd', hatch='///', zorder=-1000)
        
        # avoid double-plots (or have better resolution visualizing TMK events)
        covered[country].append( event['year'] )
        #print(country, event['year'])

if False:
    fig.savefig('fsi_tmk_vis.png', bbox_inches='tight')
fig.show()
