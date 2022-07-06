import requests

def get_quake_json():
    data = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    return data

#jsondata = data.json()