import requests
import pandas as pd
from pandas.io.json import json_normalize

def get_quake_data():
    data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    jsondata = data.json()
    return json_normalize(jsondata['features'])
