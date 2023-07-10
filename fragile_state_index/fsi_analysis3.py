#import pandas
#import seaborn as sns
from matplotlib import pyplot as plt
import pandas
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
df_tmk.replace( load_tmk.tmk_to_fsi, inplace=True )

tmk_actors = df_tmk['country'].str.split(', ')
tmk_actors_unique = np.unique( np.concatenate(tmk_actors.values) )

# replace "country" data accounting for informal comma separated lists
# in the original TMK data.
df_tmk2 = load_tmk.expand_countries(df_tmk)

# Fragile State Index 
df_fsi = load_fsi.load_joined()
load_fsi.shorten_indicators(df_fsi)

df_fsi = load_fsi.to_long(df_fsi)

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

# parameters
k = 2
L = 1

###
# Build indicator dataset on (country,year) for a TMK event.

df_p = df_tmk2.pivot_table(values='tmk', index='country', columns='year')
df_p.fillna(0., inplace=True)

# pad with non-TMK years where needed
for i in range(2006,2023 + 1):
    if i not in df_p.columns:
        df_p[i] = np.zeros(df_p.shape[0])

# pad with non-TMK countries where needed
all_fsi_countries = df_fsi['Country'].unique()
non_tmk_countries = np.setdiff1d( all_fsi_countries, df_p.index )
_df_null = pandas.DataFrame(data = np.zeros( (len(non_tmk_countries), df_p.shape[1] ) ),
                            columns = df_p.columns, 
                            index = non_tmk_countries,
)

#
df_p = df_p.append(_df_null)

X = []
y = []
# for each year i after 2006+k+L-1 (inclusive),
    # y_i : year i from TMK dataset
    # X_i : year i-L-k+1 to year i-L inclusive from the FSI dataset.
    # e.g. if k=2, L=1, then start at 2008 (prediction year); 
    # years 2008-1-2+1 (=2006) to 2008-1 (=2007) (TMI data years).




