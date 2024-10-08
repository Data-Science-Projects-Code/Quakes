import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import requests
from metrics import display_metric

# Configure the layout
st.set_page_config(layout="wide")

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
with open(css_path, "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Constants
point_opacity = 0.35
magnitude_scale = 70000
map_zoom = 1.2
gold_color = [255, 215, 0]  # Gold for fault lines and tsunami warnings
quake_color = [213, 90, 83]  # Red for normal quakes
base_color = "#2c353c"
grid_color = "#3e4044"
github_repo_url = "https://github.com/Data-Science-Projects-Code/Quakes"


@st.cache_data(ttl=600)
def load_data():
    try:
        # Fetch the list of files in the data directory
        response = requests.get(github_repo_url)
        if response.status_code != 200:
            st.error(
                f"Failed to fetch files from GitHub. Status code: {response.status_code}"
            )
            return None, None

        # Parse the JSON response
        files = response.json()
        matching_files = [file for file in files if file["name"].startswith("quakes_")]
        if not matching_files:
            st.error("No earthquake data files found.")
            return None, None

        # Sort and select the most recent file
        matching_files.sort(key=lambda x: x["name"], reverse=True)
        recent_file_url = matching_files[0]["download_url"]

        # Load the parquet file
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

        # Create duplicate dataframes for map display (duplicate + and - 360 longitude)
        quakes_plus = quakes.copy()
        quakes_plus["longitude"] = quakes_plus["longitude"] + 360
        quakes_minus = quakes.copy()
        quakes_minus["longitude"] = quakes_minus["longitude"] - 360
        quakes_map = pd.concat([quakes, quakes_plus, quakes_minus]).drop_duplicates(
            subset=["longitude", "latitude", "datetime"]
        )

        # Keep a separate dataframe for analytics (without duplicates)
        quakes_analytics = quakes.copy()

        # Load fault boundaries data and create +360 and -360 duplicates
        boundaries_url = "https://raw.githubusercontent.com/hrokr/quakes/main/data/GeoJSON/PB2002_boundaries.json"
        boundaries = gpd.read_file(boundaries_url)

        def shift_boundaries(boundaries, lon_offset):
            boundaries_shifted = boundaries.copy()
            boundaries_shifted["geometry"] = boundaries_shifted["geometry"].translate(
                xoff=lon_offset
            )
            return boundaries_shifted

        boundaries_plus = shift_boundaries(boundaries, 360)
        boundaries_minus = shift_boundaries(boundaries, -360)
        boundaries_all = pd.concat([boundaries, boundaries_plus, boundaries_minus])

        return quakes_map, quakes_analytics, boundaries_all

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


# Load data
quakes_map, quakes_analytics, boundaries = load_data()
if quakes_map is None or boundaries is None:
    st.stop()

##########
# Sidebar (Controls from File 1)
##########
st.sidebar.title("Controls")
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("Highlight tsunami warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

# Filter data for controls
pre_checkbox_filtered_quakes = quakes_analytics[
    (quakes_analytics["mag"].between(*mag_slider))
    & (quakes_analytics["depth"].between(*depth_slider))
]

# Display filtered and total rows in the sidebar
st.sidebar.text(
    f"Map & chart will display {len(pre_checkbox_filtered_quakes)} of {len(quakes_analytics)} rows"
)

# Filtered quakes for map display, using gold color for tsunami warnings
filtered_quakes = pre_checkbox_filtered_quakes.copy()
filtered_quakes["color"] = filtered_quakes["tsunami_warning"].apply(
    lambda x: gold_color if x else quake_color
)

# Title with the latest date
last_datetime = quakes_analytics["datetime"].max().strftime("%d %B %Y")
st.title(f"Earthquakes > 2.5 as of 23:59 UTC on {last_datetime}")
st.write(
    f"Displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} at depths between {depth_slider[0]} and {depth_slider[1]} km."
)

##########
# Map Visualization (from File 2)
##########
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    line_width_min_pixels=1,
    get_line_color=[255, 215, 0, 50],
    pickable=True,
    visible=toggle_boundaries,
)
# Assign color to the translated quake data (quakes_map)
quakes_map["color"] = quakes_map["tsunami_warning"].apply(
    lambda x: gold_color if x else quake_color
)

quake_layer = pdk.Layer(
    "ScatterplotLayer",
    quakes_map,  # Use quakes_map with duplicate points
    get_position=["longitude", "latitude"],
    get_radius="mag * {}".format(magnitude_scale),
    get_fill_color="color",
    opacity=point_opacity,
    pickable=True,
)

view_state = pdk.ViewState(
    longitude=-170,
    latitude=15,
    zoom=map_zoom,
    pitch=0,
)

deck = pdk.Deck(layers=[boundary_layer, quake_layer], initial_view_state=view_state)
st.pydeck_chart(deck)

##########
# DataFrame Display (from File 1)
##########
st.markdown(
    """
    <style>
    .dataframe-container {width: 100%;}
    .stDataFrame {width: 100%;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.write(
        filtered_quakes.style.set_table_attributes(
            "class='stDataFrame'"
        ).set_table_styles([{"selector": ".stDataFrame", "props": [("width", "100%")]}])
    )

##########
# Metrics (from File 1)
##########
st.markdown("---")
# Metrics for total earthquakes, intensity range, and tsunami alerts
total_quakes = len(pre_checkbox_filtered_quakes)
intensity_range = f"{pre_checkbox_filtered_quakes['mag'].min()} - {pre_checkbox_filtered_quakes['mag'].max()}"
tsunami_alerts = pre_checkbox_filtered_quakes["tsunami_warning"].sum()

# Display metrics in a row
col1, col2, col3 = st.columns(3)

with col1:
    display_metric("Total", "Total Earthquakes", (f"{total_quakes}"))
with col2:
    display_metric("Intensity", "Intensity Range", (f"{intensity_range}"))
with col3:
    display_metric("Alerts", "Tsunami Alerts", (f"{tsunami_alerts}"))

##########
# Plots (from File 2)
##########
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Depth vs Magnitude")
    plt.figure(figsize=(5.65, 6), facecolor=base_color)
    plt.scatter(
        pre_checkbox_filtered_quakes["depth"],
        pre_checkbox_filtered_quakes["mag"],
        alpha=0.5,
        c="red",
    )
    plt.title("Depth vs Magnitude")
    plt.xlabel("Depth (km)")
    plt.ylabel("Magnitude")
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)

with col2:
    st.subheader("Quake Strength by Hour")
    hist_values = np.histogram(
        pre_checkbox_filtered_quakes["datetime"].dt.hour, bins=24, range=(0, 24)
    )[0]
    plt.figure(figsize=(5.8, 6), facecolor=base_color)
    plt.bar(range(24), hist_values, color="#fe4c4b", alpha=0.60)
    plt.title("Quake Strength by Hour")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Count")
    plt.xticks(range(24))
    plt.gca().set_facecolor(base_color)
    plt.grid(color=grid_color, linestyle="--", linewidth=0.5)
    st.pyplot(plt)
