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

import numpy as np

#import seaborn
import geopandas
from matplotlib import pyplot as plt

#import datasets
#df_our = datasets.our_bootstrap_results_k1_L1()

df_our = pandas.read_csv("bootstrap_pred_results_k1_L1.csv")
df_our = df_our[df_our['year']==2022]

# aggregated scores.
scores_2022 = df_our.groupby('country').agg({"pred_prob":np.nanmean})
std_2022 = df_our.groupby('country').agg({"pred_prob":np.std})

# country boundaries via World Bank Official Boundaries;
# https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries
#

mapper = scores_2022.to_dict()['pred_prob']



gdf = geopandas.read_file('WB_Boundaries_GeoJSON_lowres/WB_countries_Admin0_lowres.geojson')

# Country name replacements only to align results
country_name_map = {'United States of America': 'United States',
             'Democratic Republic of the Congo': 'Congo Democratic Republic',
             'Republic of the Congo': 'Congo Republic',
             'Czech Republic': 'Czechia',
             "People's Republic of China": "China",
             "Ivory Coast": "Cote d'Ivoire",
             "Kyrgyzstan": "Kyrgyz Republic",
             "Guinea-Bissau": "Guinea Bissau",
             "Slovakia": "Slovak Republic",
#             "North Macedonia": 
#             "Kosovo": 
             }

    
gdf.replace(country_name_map, inplace=True)

gdf.set_index("NAME_EN", inplace=True)
gdf['scores'] = gdf.index.map(mapper)

###
# the plot
fig,ax = plt.subplots(figsize=(10,6), constrained_layout=True)
for v in ax.spines.values():
    v.set_visible(False)
ax.set(xticks=[], yticks=[])

gdf[gdf['scores'].isna()].plot(fc='#ccc', ec='#999', ax=ax, lw=0.5) # plots null/unmapped values

# TODO: (more of a dream); Peirce quinuncial projection.
# Not clear if it's possible with built-ins in geopandas right now (July 2023)
#gdf=gdf.to_crs("ESRI:54090")

gdf.plot(column='scores', cmap=plt.cm.cividis, ax=ax)

# save
fig.savefig('fsi_tmk_scoring_map_2022.png', bbox_inches='tight')
fig.savefig('fsi_tmk_scoring_map_2022.pdf', bbox_inches='tight')

