import os
import requests
import pandas as pd


def check_for_data():
    return os.path.isfile("../data/quakes_last_24.pkl")


def get_quake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    data = requests.get(url)
    jsondata = data.json()
    df = pd.json_normalize(jsondata["features"])
    return df


def save_data(df):
    df.to_pickle("../data/quakes_last_24.pkl")
