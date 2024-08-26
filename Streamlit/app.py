from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st


# Configure the layout
st.set_page_config(layout="wide")

# Constants
BASE_COLOR = "#2c353c"
GRID_COLOR = "#3e4044"
POINT_OPACITY = 0.35
MAGNITUDE_SCALE = 70000
MAP_ZOOM = 1.2


# Data loading 
@st.cache_data
def load_data():
    try:
        quakes = pd.read_parquet(
            "../data/quakes_last_24.parquet",
            engine="pyarrow",
            columns=[
                "mag",
                "place",
                "datetime",
                "longitude",
                "latitude",
                "depth",
                "tsunami warning",
            ],
        )
        boundaries = gpd.read_file("../data/geojson/pb2002_boundaries.json")
        return quakes, boundaries
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()


quakes, boundaries = load_data()


###########
# Sidebar
###########
st.sidebar.title("Controls")
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("Triggered tsunami warning")

# Data filtering
filtered_quakes = quakes[
    (quakes["mag"].between(*mag_slider)) & (quakes["depth"].between(*depth_slider))
]

# Title and display info
st.title("Earthquakes > 2.5 in the Last 24 Hours")
st.write(
    f"Displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} at depths between {depth_slider[0]} and {depth_slider[1]} km"
)

###########
# Map Visualization
###########
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
    filtered_quakes,
    get_position=["longitude", "latitude"],
    get_radius="mag * {}".format(MAGNITUDE_SCALE),
    get_fill_color=[213, 90, 83],
    opacity=POINT_OPACITY,
    pickable=True,
)

# Pydeck viewport centered on Ring of Fire
view_state = pdk.ViewState(
    latitude=15,
    longitude=-170,
    zoom=MAP_ZOOM,
    pitch=0,
)

# Render the deck 
deck = pdk.Deck(layers=[boundary_layer, quake_layer], initial_view_state=view_state)
st.pydeck_chart(deck)

###########
# Plots
###########
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Scatterplot of depth vs. magnitude
    st.subheader("Depth vs Magnitude")
    plt.figure(figsize=(5.5, 6), facecolor=BASE_COLOR)
    plt.scatter(
        filtered_quakes["depth"], filtered_quakes["mag"], alpha=0.5, c="red"
    )  # Single color for scatter plot
    plt.title("Depth vs Magnitude")
    plt.xlabel("Depth (km)")
    plt.ylabel("Magnitude")
    plt.gca().set_facecolor(BASE_COLOR)
    plt.grid(color=GRID_COLOR, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

with col2:
    # Histogram of quake strength by hour
    st.subheader("Quake Strength by Hour")
    hist_values = np.histogram(quakes["datetime"].dt.hour, bins=24, range=(0, 24))[0]
    plt.figure(figsize=(5.65, 6), facecolor=BASE_COLOR)
    plt.bar(range(24), hist_values, color="#fe4c4b", alpha=0.75)
    plt.title("Quake Strength by Hour")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Count")
    plt.grid()
    plt.xticks(range(24))
    plt.gca().set_facecolor(BASE_COLOR)
    plt.grid(color=GRID_COLOR, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

###########
# TODO List
###########
"""
TODO List:
- [x] Change dot size (scale with magnitude)
- [ ] Selectable color for quakes that generate tsunami warnings
- [x] Tweak charts to have a unified color scheme
- [x] Slider/map interactivity
- [ ] Change colors for boundaries
- [ ] Boundaries as a clickable layer
- [ ] Tweak map
"""
