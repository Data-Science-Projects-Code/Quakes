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

# # Load CSS
# with open("styles.css", "r") as css_file:
#     st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


st.markdown("<style>" + open("styles.css").read() + "</style>", unsafe_allow_html=True)


# Constants
point_opacity = 0.35
magnitude_scale = 70000
map_zoom = 1.2
gold_color = [255, 215, 0]  # Gold for fault lines and tsunami warnings
quake_color = [213, 90, 83]  # Red for normal quakes
github_repo_url = "https://api.github.com/repos/hrokr/quakes/contents/data"

@st.cache_data(ttl=600)
def load_data():
    try:
        # Fetch earthquake data
        response = requests.get(github_repo_url)
        if response.status_code != 200:
            st.error("Failed to fetch files from GitHub.")
            return None, None, None

        # Fetch recent quake file
        files = response.json()
        matching_files = [file for file in files if file["name"].startswith("quakes_")]
        matching_files.sort(key=lambda x: x["name"], reverse=True)
        recent_file_url = matching_files[0]["download_url"]

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

        # Fix to make quake locations and fault seamless by creating offset copies 
        quakes_plus = quakes.copy()
        quakes_plus["longitude"] += 360
        quakes_minus = quakes.copy()
        quakes_minus["longitude"] -= 360

        quakes_map = pd.concat([quakes, quakes_plus, quakes_minus]).drop_duplicates(
            subset=["longitude", "latitude", "datetime"])
        quakes_analytics = quakes

        boundaries_url = "https://raw.githubusercontent.com/hrokr/quakes/main/data/GeoJSON/PB2002_boundaries.json"
        boundaries = gpd.read_file(boundaries_url)

        def shift_boundaries(boundaries, lon_offset):
            boundaries_shifted = boundaries.copy()
            boundaries_shifted["geometry"] = boundaries_shifted["geometry"].translate(
                xoff=lon_offset)
            return boundaries_shifted

        boundaries_plus = shift_boundaries(boundaries, 360)
        boundaries_minus = shift_boundaries(boundaries, -360)
        boundaries_all = pd.concat([boundaries, boundaries_plus, boundaries_minus])
        return quakes_map, quakes_analytics, boundaries_all

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


quakes_map, quakes_analytics, boundaries = load_data()
if quakes_map is None or boundaries is None:
    st.stop()

##########
# Sidebar
##########
st.sidebar.title("Controls")
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))
tsunami_warning = st.sidebar.checkbox("Highlight tsunami warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

pre_checkbox_filtered_quakes = quakes_analytics[
    (quakes_analytics["mag"].between(*mag_slider))
    & (quakes_analytics["depth"].between(*depth_slider))
]

st.sidebar.text(
    f"Map & chart will display {len(pre_checkbox_filtered_quakes)} of {len(quakes_analytics)} rows"
)

# Filtered quakes for map display, all quakes show on the map but tsunami quakes are gold
filtered_quakes = pre_checkbox_filtered_quakes.copy()
filtered_quakes["color"] = filtered_quakes["tsunami_warning"].apply(
    lambda x: gold_color if x else quake_color
)

last_datetime = quakes_analytics["datetime"].max().strftime("%d %B %Y")
st.title(f"Earthquakes > 2.5 as of 23:59 UTC on {last_datetime}")
st.write(
    f"Displaying quakes between magnitude {mag_slider[0]} and {mag_slider[1]} "
    f"at depths between {depth_slider[0]} and {depth_slider[1]} km."
)

##########
# Map Visualization
##########
boundary_layer = pdk.Layer(
    "GeoJsonLayer",
    boundaries,
    line_width_min_pixels=1,
    get_line_color=[255, 215, 0, 50],
    pickable=True,
    visible=toggle_boundaries,
)

quake_layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_quakes,  
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
# DataFrame
##########
st.markdown(
    """
    <style>
    .dataframe-container {width: 100%;}
    .stDataFrame {width: 100%;}
    </style>
    """, unsafe_allow_html=True)

with st.container():
    st.write(
        filtered_quakes.style.set_table_attributes("class='stDataFrame'").set_table_styles(
            [{"selector": ".stDataFrame", "props": [("width", "100%")]}]
        )
    )


##########
# Metrics Display
##########
st.markdown("---")
# Metrics should use all data, not filtered ones to account for tsunami warnings
total_quakes = len(pre_checkbox_filtered_quakes)
intensity_range = f"{pre_checkbox_filtered_quakes['mag'].min()} - {pre_checkbox_filtered_quakes['mag'].max()}"
tsunami_alerts = pre_checkbox_filtered_quakes["tsunami_warning"].sum()

# Ensure the layout displays the metrics in a row
col1, col2, col3 = st.columns(3)

with col1:
    display_metric("Total", "Total Earthquakes", (f"{total_quakes}"))
with col2:
    display_metric("Intensity", "Intensity Range", (f"{intensity_range}"))
with col3:
    display_metric("Alerts", "Tsunami Alerts", (f"{tsunami_alerts}"))
st.markdown("---")


##########
# Plots
##########
col1, col2 = st.columns(2)

with col1:
    st.subheader("Depth vs Magnitude")
    plt.figure(figsize=(5.65, 6), facecolor="#2c353c")
    plt.scatter(pre_checkbox_filtered_quakes["depth"], pre_checkbox_filtered_quakes["mag"], alpha=0.5, c="red")
    plt.title("Depth vs Magnitude")
    plt.xlabel("Depth (km)")
    plt.ylabel("Magnitude")
    plt.gca().set_facecolor("#2c353c")
    plt.grid(color="#3e4044", linestyle="--", linewidth=0.5)
    st.pyplot(plt)

with col2:
    st.subheader("Distribution of Magnitudes")
    plt.figure(figsize=(5.65, 6), facecolor="#2c353c")
    plt.hist(pre_checkbox_filtered_quakes["mag"], bins=np.arange(2.5, 10, 0.2), color="#fe4c4b", alpha=0.6)
    plt.title("Distribution of Magnitudes")
    plt.xlabel("Magnitude")
    plt.ylabel("Frequency")
    plt.gca().set_facecolor("#2c353c")
    plt.grid(color="#3e4044", linestyle="--", linewidth=0.5)
    st.pyplot(plt)