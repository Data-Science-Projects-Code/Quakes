import requests
import pandas as pd


def get_quake_data():
    data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    jsondata = data.json()
    df = pd.json_normalize(jsondata["features"])
    return df

def remove_prefixes(df):
    return df.rename(columns=lambda x: x.replace("properties.", "").replace("geometry.", ""))

def drop_useless_cols(df):
    columns_to_drop = [
        "id", "type", "updated", "tz", "mmi", "detail", "felt", "cdi",
        "felt", "types", "nst", "type", "title"
    ]
    return df.drop(columns=columns_to_drop)
