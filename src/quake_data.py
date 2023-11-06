import os
import requests
import pandas as pd


def check_for_data():
    return os.path.isfile("../data/quake.csv")


def get_quake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    data = requests.get(url)
    jsondata = data.json()
    df = pd.json_normalize(jsondata["features"])
    return df


def remove_prefixes(df):
    return df.rename(columns=lambda x: x
             .replace("properties.", "")
             .replace("geometry.", ""))


def drop_useless_cols(df):
    columns_to_drop = [
        "id", "type", "updated", "tz", "mmi", "detail", "felt", "cdi",
        "felt", "types", "nst", "type", "title"]
    return df.drop(columns=columns_to_drop)


def save_data(df):
    df.to_csv("../data/quake.csv")
