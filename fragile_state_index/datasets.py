import load_tmk
import load_fsi
import numpy as np
import pandas

#

_df_tmk = load_tmk.load()

# Fragile State Index 
_df_fsi = load_fsi.load_joined()
load_fsi.shorten_indicators(_df_fsi)

_df_fsi = load_fsi.to_long(_df_fsi)



def build_fsi_predicting_tmk(k=2,L=1):
    '''
    Inputs:
        k: integer; number of consecutive years of FSI data to use.
            Feature vectors will be length 12k. (Default: 2)
        L: integer; years after observed data to make a prediction
            of a TMK event. L=1 corresponds to "the next year".
            (Default: 1)
    Outputs:
        X : array shape (n,12*k) of FSI data by row.
        y : array shape (n,) of TMK event data.
        meta : dictionary containing auxilliary information;
            'features' : array of strings of feature names
            
    These are designed from the perspective of performing 
    a classifcation
        
        
    '''
    df_tmk = _df_tmk[ _df_tmk['year'] >= 2006 ]
    df_tmk.replace( load_tmk.tmk_to_fsi, inplace=True )

    tmk_actors = df_tmk['country'].str.split(', ')
    tmk_actors_unique = np.unique( np.concatenate(tmk_actors.values) )


    # convert to "multi-index" pivot table; a 3D object (Country, Year, Indicator);
    # accessed first by Year; then, rows are the data for that year.
    df_fsi_pivot = _df_fsi.pivot_table(values='value', index='Country', columns=['Year','Indicator'])

    # replace "country" data accounting for informal comma separated lists
    # in the original TMK data.
    df_tmk2 = load_tmk.expand_countries(df_tmk)

    # parameters
    #k = 2
    #L = 1
    
    ###
    # Build indicator dataset on (country,year) for a TMK event.
    
    # TODO: optional variable to pass to select the column 
    # to build the pivot table out on (hence to do classification/regression on)
    df_p = df_tmk2.pivot_table(values='tmk', index='country', columns='year')
    df_p.fillna(0., inplace=True)
    
    tmk_minyear = df_p.columns.min()
    tmk_maxyear = 2023 # hard code...
    
    # pad with non-TMK years where needed
    for i in range(tmk_minyear,tmk_maxyear + 1):
        if i not in df_p.columns:
            df_p[i] = np.zeros(df_p.shape[0])
    
    # pad with non-TMK countries where needed
    all_fsi_countries = _df_fsi['Country'].unique()
    non_tmk_countries = np.setdiff1d( all_fsi_countries, df_p.index )
    _df_null = pandas.DataFrame(data = np.zeros( (len(non_tmk_countries), df_p.shape[1] ) ),
                                columns = df_p.columns, 
                                index = non_tmk_countries
                                )
    
    #
    df_p = df_p.append(_df_null)
    df_p.sort_index(inplace=True)
    
    # TODO: Code assumes row ordering is consistent.
    # CANNOT PROCEED WITH CODE AS-IS IF THIS IS NOT TRUE.
    assert all(df_p.index == df_fsi_pivot.index)
    
    #
    
    Xstack = []
    ystack = []
    countries = []
    # for each year i after 2006+k+L-1 (inclusive),
    for i in range(tmk_minyear+k+L-1, tmk_maxyear+1):
        # y_i : year i from TMK dataset
        y_i = df_p[i].values
        
        # X_i : year i-L-k+1 to year i-L inclusive from the FSI dataset.
        # array dimensions go (year, country, indicator)
        X_i = np.array([ df_fsi_pivot[i-L-k+1+j].values for j in range(k)])
        # glue together data for a single country
        X_i = np.concatenate(X_i, axis=1)
        
        # Filter out any missing data.
        to_keep = ~np.any(np.isnan(X_i), axis=1)
        
        Xstack.append( X_i[to_keep] )
        ystack.append( y_i[to_keep] )
        
        countries.append( df_p.index.values )
        # e.g. if k=2, L=1, then start at 2008 (prediction year); 
        # years 2008-1-2+1 (=2006) to 2008-1 (=2007) (TMI data years).
    #
    
    X = np.concatenate(Xstack, axis=0)
    y = np.concatenate(ystack)
    
    features_plain = df_fsi_pivot[tmk_minyear].columns.values # C1, C2, ..., S2, S1
    features = np.concatenate([['%s_Y%i'%(fp, j) for fp in features_plain] for j in range(k)])
    
    countries = np.array(countries)
    
    # must have no NaN at this point!
    assert( np.all(~np.isnan(X)) and np.all(~np.isnan(y)) )
    return X,y,{'features':features, 'countries':countries}
#