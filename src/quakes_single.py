import requests
import pandas as pd
import folium


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
# quakes["time"] = pd.to_datetime(quakes["time"], unit="ms")
# quakes["datetime"] = pd.to_datetime(quakes["time"]).dt.strftime("%Y-%m-%d %H:%M")
# quakes.drop(["time"], axis=1, inplace=True)

# fix time
quakes["time"] = pd.to_datetime(
    quakes["time"], unit="ms"
)  # Correctly convert time to datetime
quakes["datetime"] = pd.to_datetime(quakes["time"])  # Keep as datetime object
quakes.drop(["time"], axis=1, inplace=True)  # Use True here


# Split the coordinates column into longitude and latitude columns.
quakes["longitude"] = quakes.coordinates.str[0]
quakes["latitude"] = quakes.coordinates.str[1]
quakes["depth"] = quakes.coordinates.str[2]
quakes.drop(["coordinates"], axis=1, inplace=True)

# convert and relable tsunami column
quakes["tsunami warning"] = quakes["tsunami"].astype("bool")
quakes.drop(columns=["tsunami"], inplace=True)

print("Data downloaded and cleaned. Now to display it")


# Display quakes from the last 24 hours
m = folium.Map(
    location=[0, 0],
    tiles="cartodbpositron",
    zoom_start=1,
    dragging=False,
    zoom_control=False,
    scrollWheelZoom=False,
)
"""
fmtr = "function(num) {return L.Util.formatNum(num, 3);};"
folium.plugins.MousePosition(
    separator=' / ', prefix="Lat/Long: ", lat_formatter=fmtr, lng_formatter=fmtr).add_to(m)
"""

# Scale circle size to Magnitiude
for i, row in quakes.iterrows():
    folium.CircleMarker(
        (row.latitude, row.longitude),
        radius=row.mag**1.9,
        color="red",
        weight=0,
        opacity=0.4,
        fill=True,
        fill_color="orange",
        fill_opacity=0.3,
        popup=f"Time: {row.datetime},\n Mag: {row.mag},\n Depth: {row.depth} km",
    ).add_to(m)

# Add GeoJSON layer of major world fault lines

boundaries = "../data/GeoJSON/PB2002_boundaries.json"
line_style = {"color": "#FF3333", "weight": 1, "opacity": row.mag * 1.4}

folium.GeoJson(
    boundaries,
    name="major fault lines",
    style_function=lambda x: line_style,
    smooth_factor=4.0,
).add_to(m)


m.save("../images/quakes_last_24.html")
quakes.to_parquet("../data/quakes_last_24.parquet")
