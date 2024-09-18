from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import requests
from shapely.geometry import Polygon, LineString, Point

# Configure the layout
st.set_page_config(layout="wide")

# Constants
base_color = "#2c353c"
grid_color = "#3e4044"
point_opacity = 0.35
magnitude_scale = 70000
map_zoom = 1.2
github_repo_url = "https://api.github.com/repos/hrokr/quakes/contents/data"


# Data loading
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
            return None, None, None

        # Parse the JSON response
        files = response.json()

        # Filter for files that start with 'quakes_'
        matching_files = [file for file in files if file["name"].startswith("quakes_")]

        if not matching_files:
            st.error("No earthquake data files found.")
            return None, None, None

        # Sort and select the most recent file
        matching_files.sort(key=lambda x: x["name"], reverse=True)
        recent_file_url = matching_files[0]["download_url"]

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

        # Duplicate the data for map visualization by adding/subtracting 360 degrees longitude
        quakes_plus = quakes.copy()
        quakes_plus["longitude"] += 360

        quakes_minus = quakes.copy()
        quakes_minus["longitude"] -= 360

        # Quakes for map visualization (including +/- 360 longitude shifts)
        quakes_map = pd.concat([quakes, quakes_plus, quakes_minus]).drop_duplicates(
            subset=["longitude", "latitude", "datetime"]
        )

        # Use only the original quakes for analytics
        quakes_analytics = quakes

        # Load fault boundaries data
        boundaries_url = "https://raw.githubusercontent.com/hrokr/quakes/main/data/GeoJSON/PB2002_boundaries.json"
        boundaries = gpd.read_file(boundaries_url)

        # Function to shift boundaries by a longitude offset
        def shift_boundaries(boundaries, lon_offset):
            boundaries_shifted = boundaries.copy()
            boundaries_shifted["geometry"] = boundaries_shifted["geometry"].translate(
                xoff=lon_offset
            )
            return boundaries_shifted

        # Shift boundaries by +360 and -360 degrees
        boundaries_plus = shift_boundaries(boundaries, 360)
        boundaries_minus = shift_boundaries(boundaries, -360)

        # Combine original and shifted boundaries
        boundaries_all = pd.concat([boundaries, boundaries_plus, boundaries_minus])

        return quakes_map, quakes_analytics, boundaries_all

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


# Load the data
quakes_map, quakes_analytics, boundaries = load_data()
if quakes_map is None or boundaries is None:
    st.stop()

##########
# Sidebar
###########
st.sidebar.title("Controls")

# Sliders for magnitude and depth range
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))

# Filter data based on sliders (before checkbox filtering)
pre_checkbox_filtered_quakes = quakes_analytics[
    (quakes_analytics["mag"].between(*mag_slider))
    & (quakes_analytics["depth"].between(*depth_slider))
]

# Display filtered and total rows in the sidebar
st.sidebar.text(
    f"Map & chart will display {len(pre_checkbox_filtered_quakes)} of {len(quakes_analytics)} rows"
)

# Checkbox options
tsunami_warning = st.sidebar.checkbox("Highlight tsunami warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

# Further filtering based on checkboxes
filtered_quakes = pre_checkbox_filtered_quakes
if tsunami_warning:
    filtered_quakes = filtered_quakes[filtered_quakes["tsunami_warning"]]

# Title and display info
last_datetime = quakes_analytics["datetime"].max().strftime("%d %B %Y")
st.title(f"Earthquakes > 2.5 as of 23:59 UTC on {last_datetime}")

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
    get_line_color=[255, 215, 0, 50],  # RGB for #ffd700 (gold)
    pickable=True,
    visible=toggle_boundaries,  # Visibility controlled by the checkbox
)

# Quake layer with filtered data for map visualization
quake_layer = pdk.Layer(
    "ScatterplotLayer",
    quakes_map,  # Use the quakes_map for map display (including ±360 longitude quakes)
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


###########
# Display the DataFrame in a full-width container below the map
###########
with st.container():
    st.write(filtered_quakes.style.set_table_attributes("style='width: 100%;'"))


###########
# Additional Information (small boxes/charts)
###########
st.markdown("---")
total_quakes = len(filtered_quakes)
intensity_range = f"{filtered_quakes['mag'].min()} - {filtered_quakes['mag'].max()}"
tsunami_alerts = filtered_quakes["tsunami_warning"].sum()

# Custom CSS styling
st.markdown(
    """
    <style>
    .metric-box {
        background-color: #2c353c;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 30px;
        font-weight: normal;
        color: rgb(150, 76, 75);
    }
    .metric-value {
        font-size: 30px;
        font-weight: normal;
        color: rgb(250, 250, 250);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display these metrics in a row with custom styling
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Total Earthquakes</div>
            <div class="metric-value">{total_quakes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Intensity Range</div>
            <div class="metric-value">{intensity_range}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Tsunami Alerts</div>
            <div class="metric-value">{tsunami_alerts}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
