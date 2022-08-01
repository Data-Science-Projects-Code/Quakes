from tkinter import W
import requests
import pandas as pd
from pandas.io.json import json_normalize

def get_data(df):
    data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    # data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson")

    jsondata = data.json()
    quakes = pd.json_normalize(jsondata['features'])
    print(df)