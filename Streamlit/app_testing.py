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

        # Filter for files that start with 'quakes_'
        matching_files = [file for file in files if file["name"].startswith("quakes_")]

        if not matching_files:
            st.error("No earthquake data files found.")
            return None, None

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

        # Duplicate the data + and - 360 degrees longitude
        quakes_plus = quakes.copy()
        quakes_plus["longitude"] = quakes_plus["longitude"] + 360
        quakes = pd.concat([quakes, quakes_plus])

        quakes_minus = quakes.copy()
        quakes_minus["longitude"] = quakes_minus["longitude"] - 360
        quakes = pd.concat([quakes, quakes_minus])


        # Load fault boundaries data
        boundaries_url = "https://raw.githubusercontent.com/hrokr/quakes/main/data/GeoJSON/PB2002_boundaries.json"
        boundaries = gpd.read_file(boundaries_url)

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

# Sliders for magnitude and depth range
mag_slider = st.sidebar.slider("Magnitude range", 2.5, 9.9, (2.5, 9.9))
depth_slider = st.sidebar.slider("Depth range (km)", 0, 700, (0, 700))

# Filter data based on sliders (before checkbox filtering)
pre_checkbox_filtered_quakes = quakes[
    (quakes["mag"].between(*mag_slider)) & (quakes["depth"].between(*depth_slider))
]

# Display filtered and total rows in the sidebar
st.sidebar.text(
    f"Map & chart will display {len(pre_checkbox_filtered_quakes)} of {len(quakes)} rows"
)

# Checkbox options
tsunami_warning = st.sidebar.checkbox("Highlight tsunami warnings")
toggle_boundaries = st.sidebar.checkbox("Toggle Fault Boundaries")

# Further filtering based on checkboxes
filtered_quakes = pre_checkbox_filtered_quakes
if tsunami_warning:
    filtered_quakes = filtered_quakes[filtered_quakes["tsunami_warning"]]


# Title and display info - Update title to show date from parquet data
last_datetime = quakes["datetime"].max().strftime("%d %B %Y")
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

###########
# Display the DataFrame in a full-width container below the map
###########
with st.container():
    st.write(filtered_quakes.style.set_table_attributes("style='width: 100%;'"))

###########
# Additional Information (small boxes/charts)
###########

# Additional Information (small boxes/charts) with styling
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

total_quakes = len(filtered_quakes)
intensity_range = f"{filtered_quakes['mag'].min()} - {filtered_quakes['mag'].max()}"
tsunami_alerts = filtered_quakes["tsunami_warning"].sum()

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


""" 
Status: Functional
 - [ ] Update maps dynamically update.
 - [ ] Make dataframe as wide as the map (if possible)
 - [x] Recreate the updated text
 - [x] last data pull
 - [x] number of rows that match depth/magnitude
 - [x] A row with a few or so small text boxes / charts
   - [x] intensity range
   - [x] number of earthquakes that have triggered alerts
   - [ ] Maybe a box and whiskers
   - [x] Total for the day

"""
