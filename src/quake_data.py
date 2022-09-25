import requests
import pandas as pd

def get_quake_data():
    data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    jsondata = data.json()
    return pd.json_normalize(jsondata['features'])

def remove_prefixes(df):
    print(df.columns)
    v2 = df.columns.str.replace('properties.', "", regex=False)
    v3 = v2.columns.str.replace('geometry.', "", regex=False)
    print(v2)
    print("and now for the last step")
    print(v3)
    return(df)
    
def drop_useless_cols(df):    
    # quake_data.drop(['id', 'type', 'updated', 'tz', 'mmi', 'detail', 'felt','cdi', 'felt', 'types', 'nst', 'type', 'title'], axis=1, inplace=True)
    #print(quake_data.columns)
    return quake_data
