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



def build_fsi_predicting_tmk(k=2,L=1, min_year=2006, max_year=2023, track_ongoing=True, target='tmk'):
    '''
    Inputs:
        k: integer; number of consecutive years of FSI data to use.
            Feature vectors will be length 12k. (Default: 2)
        L: integer; years after observed data to make a prediction
            of a TMK event. L=1 corresponds to "the next year".
            (Default: 1)
        min_year: integer (default: 2006)
        max_year: integer (default: 2023)
        track_ongoing: boolean (default: True).
        target: string, name of column in TMK to predict (default: tmk)
            Here, may also consider tmk.ordinal which is a relative 
            numerical score for severity of the TMK event.
        
    Outputs:
        X : array shape (n,12*k) of FSI data by row.
        y : array shape (n,) of TMK event data.
        meta : dictionary containing auxilliary information;
            'features' : array of strings of feature names
            
    These are designed from the perspective of performing 
    a classification; the outputs are numerical arrays X, y, and 
    associated metadata for each row.
    
    The "track_ongoing" flag controls whether data for a country 
    should be included if they had a TMK event in the past k years; 
    this comes from the perspective of pre-emption (the types of 
    actions that can be taken are very different before and after 
    an event has taken place.)
    '''
    df_tmk = _df_tmk[ _df_tmk['year'] >= min_year]
    
    # TODO: adjust to make warnings go away.
    df_tmk.replace( load_tmk.tmk_to_fsi, inplace=True )

    # convert to "multi-index" pivot table; a 3D object (Country, Year, Indicator);
    # accessed first by Year; then, rows are the data for that year.
    df_fsi_pivot = _df_fsi.pivot_table(values='value', index='Country', columns=['Year','Indicator'])

    # replace "country" data accounting for informal comma separated lists
    # in the original TMK data.
    df_tmk2 = load_tmk.expand_countries(df_tmk)
    
    ###
    # Build indicator dataset on (country,year) for a TMK event.
    
    # TODO: optional variable to pass to select the column 
    # to build the pivot table out on (hence to do classification/regression on)
    df_p = df_tmk2.pivot_table(values=target, index='country', columns='year')
    df_p.fillna(0., inplace=True)
    
    tmk_minyear = df_p.columns.min()
    tmk_maxyear = max_year
    
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
    
    tmk_only_long = df_p.melt(ignore_index=False)
    tmk_only_long = tmk_only_long[tmk_only_long['value']==1]
    
    # record (country, year) values if we want to not do prediction 
    # on ongoing events.
    tmk_country_years = list(zip(tmk_only_long.index, tmk_only_long['year']))
    
    # TODO: Code assumes row ordering is consistent.
    # CANNOT PROCEED WITH CODE AS-IS IF THIS IS NOT TRUE.
    assert all(df_p.index == df_fsi_pivot.index)
    
    #
    
    Xstack = []
    ystack = []
    countries = []
    years = []
    
    tmk_events_tracked = []
    
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
        
        if not track_ongoing:
            teck = np.nonzero(y_i)[0] # tmk event country indices for year i.
            for _z in teck:
                event = (df_p.index.values[_z], i)
                if not is_not_ongoing(event, tmk_country_years, k=k):
                    to_keep[_z] = False
                else:
                    tmk_events_tracked.append(event)
        #
        Xstack.append( X_i[to_keep] )
        ystack.append( y_i[to_keep] )
        
        countries.append( df_p.index.values[to_keep] )
        years.append( np.repeat(i, len(countries[-1])) )
        
        # e.g. if k=2, L=1, then start at 2008 (prediction year); 
        # years 2008-1-2+1 (=2006) to 2008-1 (=2007) (TMI data years).
    #
    
    X = np.concatenate(Xstack, axis=0)
    y = np.concatenate(ystack)
    
    features_plain = df_fsi_pivot[tmk_minyear].columns.values # C1, C2, ..., S2, S1
    features = np.concatenate([['%s_Y%i'%(fp, j) for fp in features_plain] for j in range(k)])

    print(tmk_events_tracked)
    print(len(tmk_events_tracked))    

    # must have no NaN at this point!
    assert( np.all(~np.isnan(X)) and np.all(~np.isnan(y)) )
    return X,y,{'features':features, 'countries':countries, 'years':years}
#

def is_not_ongoing(event, prior_event_list, k=1, L=1):
    '''
    Returns boolean whether or not a (country,year) we are trying to predict on 
    has had another TMK event in the past k+L years.
    
    Inputs:
        event: tuple (country, year)
        prior_event_list: list of tuples of the form (country, year)
        k, L: integers; in same 
        L: 
    Outputs:
        True/False; True meaning the event can be included.
    
    For example, if (Australia, 2013) was the input with k=1, L=1, then 
    we are trying to predict a TMK in 2013 in the year 2013-L=2012. 
    We would not want to try to predict this if there was a TMK event in 
    2012-k+1=2012.
    
    So, if the data set had 
        (Australia, 2012),
    the function would return False.
    
    For another example, if inputs were (Chad, 2020), k=2, L=2, 
    then we want to make the prediction from 2020-L=2018. We 
    incorporate k years worth of data; 2018-k+1 = 2017. 
    Hence, we would not include this new event if either of 
    (Chad, 2017) or (Chad, 2018) were in the prior_event_list.
    
    '''
    t = event[1]-L+1
    for i in range(t-k, t):
        if (event[0], i) in prior_event_list:
            return False
    return True

