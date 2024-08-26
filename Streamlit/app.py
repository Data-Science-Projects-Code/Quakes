from datetime import datetime
import geopandas as gpd
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

columns = [
    "mag",
    "place",
    "datetime",
    "longitude",
    "latitude",
    "depth",
    "tsunami warning",
]

quakes = pd.read_parquet(
    "../data/quakes_last_24.parquet", engine="pyarrow", columns=columns
)

# Load GeoJSON boundaries
boundaries = gpd.read_file("../data/geojson/pb2002_boundaries.json")

st.title("Earthquakes > 2.5 Last 24 Hours")

# Create Pydeck layers (leave this part commented out for now)
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    get_fill_color=[255, 0, 0, 150],
    get_line_color=[0, 0, 0],
    line_width_min_pixels=1,
    pickable=True,
)

quake_layer = pdk.Layer(
    "ScatterplotLayer",
    quakes,
    get_position=["longitude", "latitude"],
    get_radius="mag * 10000",
    get_fill_color="[255 * (1 - mag / 10), 0, 255 * (mag / 10), 140]",
    pickable=True,
)

# Create a Pydeck viewport centered on your area of interest
view_state = pdk.ViewState(
    latitude=quakes["latitude"].mean(),
    longitude=quakes["longitude"].mean(),
    zoom=1.1,
    pitch=0,
)

# Create a Pydeck Deck instance (leave this part commented out for now)
deck = pdk.Deck(layers=[boundary_layer, quake_layer], initial_view_state=view_state)

# Render the deck in Streamlit (leave this part commented out for now)
st.pydeck_chart(deck)
 

###########
# Sidebar
###########
st.sidebar.title("Controls")

mag_slider = st.sidebar.slider(
    "Magnitude range", min_value=2.5, max_value=9.9, value=[2.5, 9.9]
)
depth_slider = st.sidebar.slider("Depth range (km)", value=[0, 700])
tsunami_warning = st.sidebar.checkbox("Triggered tsunami warning")

# Preparing data for filtering based on sidebar inputs
filtered_quakes = quakes[
    (quakes["mag"] >= mag_slider[0])
    & (quakes["mag"] <= mag_slider[1])
    & (quakes["depth"] >= depth_slider[0])
    & (quakes["depth"] <= depth_slider[1])
]
st.markdown("---")
st.subheader("Metrics")
st.markdown("---")  

# Use side by side layout
col1, col2 = st.columns(2)

with col1:
    # Scatterplot of depth vs. magnitude
    st.subheader("Depth vs Magnitude")
    plt.figure(figsize=(6, 6))
    plt.scatter(filtered_quakes["depth"], filtered_quakes["mag"], alpha=0.5)
    plt.title("Depth vs Magnitude")
    plt.xlabel("Depth (km)")
    plt.ylabel("Magnitude")
    plt.grid()
    st.pyplot(plt)

with col2:
    # Histogram of quake strength by hour
    st.subheader("Quake Strength by Hour")
    hist_values = np.histogram(quakes["datetime"].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

"""
TODO List

- [ ] change dot size (scale with magnitude)
- [ ] selectable color for quakes that generate tsunami warning 
- [ ] tweak charts to have a unified color scheme
- [ ] slider/map interactivity
- [ ] change colors for boundaries
- [ ] boundaries as a clickable layer

"""