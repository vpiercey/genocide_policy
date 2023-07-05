
import os
import pandas

DATA_FOLDER = os.path.abspath('../data')

def load(folder=DATA_FOLDER):
    fname = os.path.join(DATA_FOLDER, 'tmk_events_release_1.1.xls')
    df = pandas.read_excel(fname)
    
    #df['country'].fillna('', inplace=True)
    mask = df['country'].notna()
    df = df[mask]
    df['country'] = df['country'].str.strip()
    return df
