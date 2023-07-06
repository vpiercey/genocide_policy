import pandas
import seaborn as sns
import load_fsi
from matplotlib import pyplot as plt

sns.set_theme()
plt.rcParams.update({'font.size': 20})

#
# Load data

df = load_fsi.load_joined()
load_fsi.shorten_indicators(df)

df_long = load_fsi.to_long(df)


# taking a handful of countries and 
# indicators to visualize out-of-the-box...

countries = [
    'Switzerland',    
    'United States',
    'Sudan',
    'Serbia',
    'China'
]

# see https://fragilestatesindex.org/indicators/
# C3: Group Grievance
# E1: Economic Decline
# P2: Public Services
# P3: Human Rights and Rule of Law
indicators = [
    'C3',
    'E1',
    'P2',
    'P3',
]

mask = df_long['Country'].isin(countries)
mask2 = df_long['Indicator'].isin(indicators)
df_sub = df_long[mask*mask2]


# mimicking 
# https://seaborn.pydata.org/examples/many_facets.html
#

grid = sns.FacetGrid(
    df_sub,
    col='Country',
    row='Indicator',
    hue='Country',
    palette='tab10',
    margin_titles=True
)

grid.map(plt.plot, "Year", "value", marker="o", lw=2, markersize=10)

# TODO: increase font size.
# pyplot rcParams don't seem to affect facetgrid.

grid.fig.suptitle("FSI indicators", x=0, ha='left')
grid.fig.subplots_adjust(top=0.92) # shift down to make title visible

if False:
    grid.fig.savefig('fsi_example.png', bbox_inches='tight')
