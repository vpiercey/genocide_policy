#
# Load Fragile State Index data.
#
# Note: some manual renaming of 
# the 2022/2023 files were done to 
# match the syntax of prior years.
#
# Note: these are xlsx files, so 
# you may need to install another 
# package to support it.
# See the conglomerated file/script
# for a csv version which joins all 
# years' data.

import os
import pandas

DATA_FOLDER = os.path.abspath('../data')

def load(folder=DATA_FOLDER):
    '''
    Loads Fragile State Index data as a single 
    pandas dataframe. 
    
    You MUST rename 2022 and 2023 data files to match 
    the convention of 2006-2021 or this script will fail.
    
    Input:
        folder : string; where raw data is located (default: data/)
    Output:
        df : pandas dataframe; contains all years' data.
    '''
    folder = os.path.dirname( os.path.abspath(folder) )
    folder = os.path.join(folder, 'data')
    
    dfs = []
    for i in range(2006, 2023+1): # TODO: switch to glob.glob on filename
        fname = os.path.join(folder, 'fsi-%i.xlsx'%i)
        df = pandas.read_excel(fname)
        df['Year'] = i # correct misinterpreted data type
        df['Country'] = df['Country'].str.strip() # remove trailing whitespace
        dfs.append(df)
    
    df = pandas.concat(dfs, axis=0, ignore_index=True)
    df.drop(columns=['Change from Previous Year'], inplace=True)
    
    # country name "Kyrgyzstan" only has data for 2021-2022;
    # "Kyrgyz Republic" is complete. 
    # No apparent difference in country sovereignty.
    # Similarly for Slovakia vs Slovak Republic.
    # Other exclusions can be put here later as well.
    df = df[ ~ df['Country'].isin( 
        ['Kyrgyzstan','Slovakia']
        )
        ]
    
    return df

def create_joined(fname='fsi_2006-2023.csv', folder=DATA_FOLDER):
    '''
    Creates a CSV file of the joined data. If already created, bypasses 
    the need for an xlsx compatible loader for pandas.
    
    Inputs:
        fname : string; name of output file (default: fsi_2006-2003.csv)
        folder : string; location of the raw FSI data (passed on to load())
    '''
    df = load(folder=folder)
    try:
        path = os.path.abspath(fname)
        df.to_csv(path, index=None)
        print('Success')
        print('')
        print('File written to %s'%path)
    except:
        print('Failure')
    return

def load_joined(fname='fsi_2006-2023.csv'):
    df = pandas.read_csv(fname)
    return df

def indicator_list():
    ll = [
        "C1: Security Apparatus",
        "C2: Factionalized Elites",
        "C3: Group Grievance",
        "E1: Economy",
        "E2: Economic Inequality",
        "E3: Human Flight and Brain Drain",
        "P1: State Legitimacy",
        "P2: Public Services",
        "P3: Human Rights",
        "S1: Demographic Pressures",
        "S2: Refugees and IDPs",
        "X1: External Intervention"
    ]
    return ll

def indicator_list_short():
    ll = [
        'C1', 'C2', 'C3', 
        'E1', 'E2', 'E3', 
        'P1', 'P2', 'P3', 
        'S1', 'S2', 'X1']
    return ll

def shorten_indicators(mydf):
    ll = indicator_list()
    if 'Indicator' in mydf.columns:
        mydf.replace(
            to_replace={s: s.split(':')[0] for s in ll},
            inplace=True
            )
    else:
        mydf.rename(
            columns={s: s.split(':')[0] for s in ll},
            inplace=True
            )
    return

def to_long(mydf):
    import numpy as np
    
    all_vars = mydf.columns
    
    indicators = np.setdiff1d( all_vars, ['Country', 'Year', 'Rank', 'Total'] )
    
    df_long = pandas.melt(
        mydf,
        id_vars=['Country', 'Year'],
        value_vars=indicators,
        var_name='Indicator'
    )
    
    # add super-categories
    df_long['Indicator_group'] = [s[0] for s in df_long['Indicator']]
    df_long.replace({'X':'S'}, inplace=True)
    
    return df_long

if __name__=="__main__":
    create_joined()
