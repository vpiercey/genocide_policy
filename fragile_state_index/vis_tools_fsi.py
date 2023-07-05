
from matplotlib import pyplot as plt
from matplotlib import ticker
import seaborn as sns
import load_fsi

indicator_palette_12 = sns.color_palette(
    palette=[
        plt.cm.tab20c(i) for i in [0,1,2, 4,5,6, 8,9,10, 12,13,14]
        ]
    )
indicator_palette_4 = sns.color_palette(
    palette=[
        plt.cm.tab20c(i) for i in range(0,16,4)
        ]
    )

def profile_country(mydf, country, ax):
    '''
    Plots time series in the given pyplot axis,
    for all indicators for the 
    given country, given the LONG FORM dataframe 
    (must have a column named "Indicator").
    
    Inputs:
        mydf: FSI pandas dataframe; after conversion to long format
            (see load_fsi.to_long())
        country: string; country name
        ax: pyplot axis to make plot
    '''
    _lp = sns.lineplot(mydf[mydf['Country']==country], x='Year', y='value', hue='Indicator', palette=indicator_palette_12, ax=ax, lw=3, legend="brief", estimator=None)
    ax.set_title(country, loc='left')
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_ylim(0,10)
    sns.move_legend(_lp, "upper left")
    
    return _lp


def profile_country_brief(mydf, country, ax):
    '''
    Plots time series in the given pyplot axis.
    given country, given the LONG FORM dataframe 
    (must have a column named "Indicator").
    
    Data is averaged by the indicator category (4 curves instead of 12).
    
    Inputs:
        mydf: FSI pandas dataframe; after conversion to long format
            (see load_fsi.to_long())
        country: string; country name
        ax: pyplot axis to make plot
    '''
    _lp = sns.lineplot(mydf[mydf['Country']==country], x='Year', y='value', hue='Indicator_group', palette=indicator_palette_4, ax=ax, lw=5, legend="brief", estimator="mean", errorbar=None)
    ax.set_title(country, loc='left')
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_ylim(0,10)
    sns.move_legend(_lp, "upper left")
    
    return _lp

if __name__=="__main__":
    
    sns.set_theme(style='whitegrid')
    
    df = load_fsi.load_joined()
    df_long = load_fsi.to_long(df)
    load_fsi.shorten_indicators(df_long)
    
    #
    fig,ax = plt.subplots(2,3, figsize=(12,8), 
                          sharex=True, sharey=True, constrained_layout=True)
    
    profile_country(df_long, 'United States', ax[0,0])
    profile_country(df_long, 'Canada', ax[0,1])
    profile_country(df_long, 'Mexico', ax[0,2])
    
    #
    profile_country_brief(df_long, 'United States', ax[1,0])
    profile_country_brief(df_long, 'Canada', ax[1,1])
    profile_country_brief(df_long, 'Mexico', ax[1,2])
    
    #
    for i in range(2):
        ax[0,i].get_legend().set_visible(False)
        ax[1,i].get_legend().set_visible(False)       

