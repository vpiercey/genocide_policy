
import os
import pandas

DATA_FOLDER = os.path.abspath('../data')

# manual codings from TMK country names to FSI country names
tmk_to_fsi = {
    'DR Congo (Zaire)': 'Congo Democratic Republic',
    'Ivory Coast': "Cote d'Ivoire",
    'Myanmar (Burma)': "Myanmar"
}

def load(folder=DATA_FOLDER):
    fname = os.path.join(DATA_FOLDER, 'tmk_events_release_1.1.xls')
    df = pandas.read_excel(fname)
    
    #df['country'].fillna('', inplace=True)
    mask = df['country'].notna()
    df = df[mask]
    df['country'] = df['country'].str.strip()
    
    df.replace(tmk_to_fsi, inplace=True)
    
    return df

def expand_countries(mydf):
    '''
    Expand on column "country", duplicating unique rows for 
    each country. 
    
    CAUTION: as of 6 July, other columns which contain information 
        about the instigator, government or non-government actors, 
        etc, gets confused/lost as these get mindlessly copied.
        Is a TODO to be more careful about the expansion happening here.
    
    (Conflict names recoverable via column "tmk_id"... I think?)
    
    Input:
        mydf : dataframe; the result of load()
    Output:
        df_ucountry : dataframe processed in the manner described above.
    '''
    rows = []
    for row in mydf.iloc:
        for e in row['country'].split(', '):
            newrow = row.copy()
            newrow['country'] = e
            rows.append(newrow)
    df_ucountry = pandas.DataFrame(rows)
    return df_ucountry