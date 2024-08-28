import requests
import pandas as pd

data = requests.get(
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
)
jsondata = data.json()
quakes = pd.json_normalize(jsondata["features"])

# Truncate some of the names and drop useless columns
quakes.columns = quakes.columns.str.replace("properties.", "", regex=False)
quakes.columns = quakes.columns.str.replace("geometry.", "", regex=False)
quakes.drop(
    [
        "id",
        "type",
        "updated",
        "tz",
        "mmi",
        "detail",
        "felt",
        "cdi",
        "felt",
        "types",
        "nst",
        "type",
        "title",
    ],
    axis=1,
    inplace=True,
)

# Strip out leading and trailing commas from 'ids' and 'sources' fields
quakes["ids"] = quakes["ids"].str.strip(",")
quakes["sources"] = quakes["sources"].str.strip(",")

# Fix time
quakes["time"] = pd.to_datetime(quakes["time"], unit="ms") 
quakes["datetime"] = pd.to_datetime(quakes["time"])
quakes.drop(["time"], axis=1, inplace=True)

# Split the coordinates column into longitude and latitude columns.
quakes["longitude"] = quakes.coordinates.str[0]
quakes["latitude"] = quakes.coordinates.str[1]
quakes["depth"] = quakes.coordinates.str[2]
quakes.drop(["coordinates"], axis=1, inplace=True)

# convert and relabel tsunami column
quakes["tsunami warning"] = quakes["tsunami"].astype("bool")
quakes.drop(columns=["tsunami"], inplace=True)

print("Data downloaded, cleaned, and saved as a parquet file.")
quakes.to_parquet("../data/quakes_last_24.parquet")