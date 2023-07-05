
from matplotlib import pyplot as plt
from matplotlib import ticker
import seaborn as sns
import load_fsi

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
    sns.lineplot(mydf[mydf['Country']==country], x='Year', y='value', hue='Indicator', ax=ax, marker='o', legend=False)
    ax.set_title(country, loc='left')
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_ylim(0,10)
    
    return

if __name__=="__main__":
    
    df = load_fsi.load_joined()
    df_long = load_fsi.to_long(df)
    load_fsi.shorten_indicators(df_long)
    
    
    fig,ax = plt.subplots(1,3, figsize=(12,4), 
                          sharex=True, sharey=True, constrained_layout=True)
    
    profile_country(df_long, 'United States', ax[0])
    profile_country(df_long, 'Canada', ax[1])
    profile_country(df_long, 'Mexico', ax[2])
