from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import requests

# Configure the layout
st.set_page_config(layout="wide")

# Constants
base_color = "#2c353c"
grid_color = "#3e4044"
point_opacity = 0.35
magnitude_scale = 70000
map_zoom = 1.2
github_repo_url = "https://api.github.com/repos/hrokr/quakes/contents/data"


# Data loading with debugging statements
@st.cache_data(ttl=600)
def load_data():
    try:
        # Fetch the list of files in the data directory
        response = requests.get(github_repo_url)
        if response.status_code != 200:
            st.error(
                "Failed to fetch files from GitHub. Status code: {}".format(
                    response.status_code
                )
            )
            return None, None

        # Parse the JSON response
        files = response.json()
        st.write("Files fetched from GitHub:", files)  # Debugging statement

        # Filter for files that start with 'quakes_'
        matching_files = [file for file in files if file["name"].startswith("quakes_")]
        st.write(
            "Matching earthquake data files:", matching_files
        )  # Debugging statement

        if not matching_files:
            st.error("No earthquake data files found.")
            return None, None

        # Sort and select the most recent file
        matching_files.sort(key=lambda x: x["name"], reverse=True)
        recent_file_url = matching_files[0]["download_url"]
        st.write("Fetching data from URL:", recent_file_url)  # Debugging statement

        # Load the parquet file from the URL
        quakes = pd.read_parquet(
            recent_file_url,
            engine="pyarrow",
            columns=[
                "datetime",
                "longitude",
                "latitude",
                "place",
                "mag",
                "depth",
                "tsunami_warning",
            ],
        )
        st.write("Earthquake data loaded:", quakes.head())  # Debugging statement

        # Update the boundaries URL to point to the correct path with proper casing
        boundaries_url = "https://raw.githubusercontent.com/hrokr/quakes/main/data/GeoJSON/PB2002_boundaries.json"
        st.write("Fetching boundaries from URL:", boundaries_url)  # Debugging statement
        boundaries = gpd.read_file(boundaries_url)
        st.write("Boundaries data loaded: True")  # Debugging statement

        return quakes, boundaries

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


quakes, boundaries = load_data()
if quakes is None or boundaries is None:
    st.stop()

##########
# Sidebar
###########
st.sidebar.title("Controls")
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("Highlight tsunami warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

# Data filtering
filtered_quakes = quakes[
    (quakes["mag"].between(*mag_slider)) & (quakes["depth"].between(*depth_slider))
]
if tsunami_warning:
    filtered_quakes = filtered_quakes[filtered_quakes["tsunami_warning"]]

st.write(f"Filtered earthquakes: {len(filtered_quakes)} rows")  # Debugging statement

# Title and display info
st.title("Earthquakes > 2.5 in the Last 24 Hours")
st.write(
    f"Displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} "
    f"at depths between {depth_slider[0]} and {depth_slider[1]} km."
)

###########
# Map Visualization
###########
# Boundary layer visibility depends on the toggle_boundaries checkbox
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    line_width_min_pixels=1,
    get_line_color=[255, 215, 0, 50],  # RGB for #ffd700
    pickable=True,
    visible=toggle_boundaries,  # Visibility controlled by the checkbox
)
st.write("Boundary layer created.")  # Debugging statement

# Quake layer with filtered data
quake_layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_quakes,
    get_position=["longitude", "latitude"],
    get_radius="mag * {}".format(magnitude_scale),
    get_fill_color=[213, 90, 83],  # Single color for all quakes
    opacity=point_opacity,
    pickable=True,
)

# Pydeck viewport centered on the Ring of Fire
view_state = pdk.ViewState(
    longitude=-170,
    latitude=15,
    zoom=map_zoom,
    pitch=0,
)

# Render the deck
deck = pdk.Deck(
    layers=[boundary_layer, quake_layer],
    initial_view_state=view_state,
)
st.pydeck_chart(deck)
st.write("Boundary layer added to layers.")  # Debugging statement

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
        filtered_quakes["depth"], filtered_quakes["mag"], alpha=0.5, c="red"
    )  # Single color for scatter plot
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
Todo List:
- [x] Change dot size (scale with magnitude)
- [x] Selectable color for quakes that generate tsunami warnings
- [x] Tweak charts to have a unified color scheme
- [x] Slider/map interactivity
- [x] Change colors for boundaries
- [ ] Boundaries as a clickable layer
- [ ] Tweak map
"""
