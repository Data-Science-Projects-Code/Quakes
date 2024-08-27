import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st

# Configure the layout
st.set_page_config(layout="wide")

# Constants
base_color = "#2c353c"
grid_color = "#3e4044"
point_opacity = 0.8
magnitude_scale = 70000
map_zoom = 1.2


# Data loading
@st.cache_data
def load_data():
    try:
        quakes = pd.read_parquet(
            "../data/quakes_last_24.parquet",
            engine="pyarrow",
            columns=[
                "datetime",
                "longitude",
                "latitude",
                "place",
                "mag",
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

##########
# Sidebar
###########
st.sidebar.title("Controls")
mag_slider = st.sidebar.slider("Magnitude Range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth Range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("Highlight Tsunami Warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

# Data filtering
filtered_quakes = quakes[
    (quakes["mag"].between(*mag_slider)) & (quakes["depth"].between(*depth_slider))
]

# Title and display info
st.title("Earthquakes > 2.5 in the Last 24 Hours")
st.write(
    f"Displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} at depths between {depth_slider[0]} and {depth_slider[1]} km"
)

# Selection for DataFrame row with 'None Selected' as default
quake_select = st.sidebar.selectbox(
    "Select an earthquake:", ["None Selected"] + filtered_quakes.index.tolist()
)

###########
# Map Visualization
###########

# Create layers for the map
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    lineWidthMinPixels=1,
    getLineColor=[255, 215, 0, 50],  # RGB for #ffd700
    pickable=True,
    visible=toggle_boundaries,
)

# Determine fill colors based on selection
quake_layer_data = filtered_quakes.copy()
quake_layer_data["color"] = [
    [0, 255, 0, 70]
    if idx == quake_select and quake_select != "None Selected"
    else [213, 90, 83, 85]
    for idx in quake_layer_data.index
]

# Create the quake layer with the tooltip
quake_layer = pdk.Layer(
    "ScatterplotLayer",
    quake_layer_data,
    getPosition=["longitude", "latitude"],
    getRadius="mag * {}".format(magnitude_scale),
    getFillColor="color",  # Use the color column created based on selection
    opacity=point_opacity,
    pickable=True,
    tooltip={
        "html": "<b>Place:</b> {place}<br><b>Magnitude:</b> {mag}<br><b>Depth:</b> {depth} km",
        "style": {"color": "white", "backgroundColor": "rgba(0, 0, 0, 1)"},
    },
)

# Pydeck viewport centered on the Ring of Fire
view_state = pdk.ViewState(
    longitude=-170,
    latitude=15,
    zoom=map_zoom,
    pitch=0,
)

# Render the deck in a full-width container
with st.container():
    deck = pdk.Deck(layers=[boundary_layer, quake_layer], initial_view_state=view_state)
    st.pydeck_chart(deck)

# Display the DataFrame in a full-width container below the map
with st.container():
    st.write(filtered_quakes.style.set_table_attributes("style='width: 100%;'"))

###########
# Plots
###########
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Scatterplot of depth vs. magnitude
    st.subheader("Depth vs Magnitude")
    plt.figure(figsize=(5.65, 6), facecolor=base_color)
    plt.scatter(
        filtered_quakes["depth"], filtered_quakes["mag"], alpha=0.5, color="#fe4c4b")
    plt.title("Depth vs Magnitude")
    plt.xlabel("Depth (km)")
    plt.ylabel("Magnitude")
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

with col2:
    # Histogram of quake strength by hour
    st.subheader("Quake Strength by Hour")
    hist_values = np.histogram(
        filtered_quakes["datetime"].dt.hour, bins=24, range=(0, 24)
    )[0]
    plt.figure(figsize=(5.8, 6), facecolor=base_color)
    plt.bar(range(24), hist_values, color="#fe4c4b", alpha=0.60)
    plt.title("Quake Strength by Hour")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Count")
    plt.grid()
    plt.xticks(range(24))
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

###########
# Todo List
###########
"""
todo items:
- [x] change dot size (scale with magnitude)
- [x] selectable color for quakes that generate tsunami warnings
- [x] tweak charts to have a unified color scheme
- [x] slider/map interactivity
- [x] change colors for boundaries
- [x] boundaries as a clickable layer
- [x] display dataframe
- [x] make dataframe the same width as map
- [x] integrated tooltip functionality for markers
- [x] visually distinguish selected quakes using colors
- [ ] tweak map -- updating on pan
- [ ] dataframe/map interaction
"""
