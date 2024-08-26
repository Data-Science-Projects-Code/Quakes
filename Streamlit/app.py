from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st

# configure the layout
st.set_page_config(layout="wide")

# constants
base_color = "#2c353c"
grid_color = "#3e4044"
point_opacity = 0.35
magnitude_scale = 70000
map_zoom = 1.2


# data loading
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
        st.error(f"error loading data: {e}")
        st.stop()


quakes, boundaries = load_data()

###########
# sidebar
###########
st.sidebar.title("controls")
mag_slider = st.sidebar.slider("magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("depth range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("triggered tsunami warning")

# data filtering
filtered_quakes = quakes[
    (quakes["mag"].between(*mag_slider)) & (quakes["depth"].between(*depth_slider))
]
if tsunami_warning:
    filtered_quakes = filtered_quakes[filtered_quakes["tsunami warning"]]

# title and display info
st.title("earthquakes > 2.5 in the last 24 hours")
st.write(
    f"displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} at depths between {depth_slider[0]} and {depth_slider[1]} km"
)

###########
# map visualization
###########
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    line_width_min_pixels=1,
    get_line_color=[255, 215, 0, 50],  # RGB for #ffd700
    pickable=True,
)

quake_layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_quakes,
    get_position=["longitude", "latitude"],
    get_radius="mag * {}".format(magnitude_scale),
    get_fill_color=[213, 90, 83],
    opacity=point_opacity,
    pickable=True,
)

# pydeck viewport centered on ring of fire
view_state = pdk.ViewState(
    longitude=-170,
    latitude=15,
    zoom=map_zoom,
    pitch=0,
)

# render the deck
deck = pdk.Deck(layers=[boundary_layer, quake_layer], initial_view_state=view_state)
st.pydeck_chart(deck)

###########
# plots
###########
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # scatterplot of depth vs. magnitude
    st.subheader("depth vs magnitude")
    plt.figure(figsize=(5.5, 6), facecolor=base_color)
    plt.scatter(
        filtered_quakes["depth"], filtered_quakes["mag"], alpha=0.5, c="red"
    )  # single color for scatter plot
    plt.title("depth vs magnitude")
    plt.xlabel("depth (km)")
    plt.ylabel("magnitude")
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

with col2:
    # histogram of quake strength by hour
    st.subheader("quake strength by hour")
    hist_values = np.histogram(
        filtered_quakes["datetime"].dt.hour, bins=24, range=(0, 24)
    )[0]
    plt.figure(figsize=(5.65, 6), facecolor=base_color)
    plt.bar(range(24), hist_values, color="#fe4c4b", alpha=0.75)
    plt.title("quake strength by hour")
    plt.xlabel("hour of the day")
    plt.ylabel("count")
    plt.grid()
    plt.xticks(range(24))
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

###########
# todo list
###########
"""
todo list:
- [x] change dot size (scale with magnitude)
- [x] selectable color for quakes that generate tsunami warnings
- [x] tweak charts to have a unified color scheme
- [x] slider/map interactivity
- [x] change colors for boundaries
- [ ] boundaries as a clickable layer
- [ ] tweak map
"""
