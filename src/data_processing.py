import requests
import pandas as pd
import logging
from datetime import datetime
import os

# Get the top-level directory (parent of src)
top_level_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Set up log and data directories at the top level
log_dir = os.path.join(top_level_dir, "logs")
data_dir = os.path.join(top_level_dir, "data")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(
        log_dir, f'data_processing_{datetime.utcnow().strftime("%Y-%m-%d")}.log'
    ),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Data processing script started.")

try:
    data = requests.get(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    )
    jsondata = data.json()
    quakes = pd.json_normalize(jsondata["features"])

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

    quakes["ids"] = quakes["ids"].str.strip(",")
    quakes["sources"] = quakes["sources"].str.strip(",")

    quakes["time"] = pd.to_datetime(quakes["time"], unit="ms")
    quakes["datetime"] = pd.to_datetime(quakes["time"])
    quakes.drop(["time"], axis=1, inplace=True)

    quakes["longitude"] = quakes.coordinates.str[0]
    quakes["latitude"] = quakes.coordinates.str[1]
    quakes["depth"] = quakes.coordinates.str[2]
    quakes.drop(["coordinates"], axis=1, inplace=True)

    quakes["tsunami warning"] = quakes["tsunami"].astype("bool")
    quakes.drop(columns=["tsunami"], inplace=True)

    logging.info("Data downloaded and cleaned successfully.")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_filename = os.path.join(data_dir, f"quakes_{today}.parquet")
    quakes.to_parquet(daily_filename)
    logging.info(f"Today's data saved as {daily_filename}.")

    aggregated_filename = os.path.join(data_dir, "aggregated_data.parquet")
    try:
        aggregated_data = pd.read_parquet(aggregated_filename)
        aggregated_data = pd.concat([aggregated_data, quakes], ignore_index=True)
        logging.info(f"Appended today's data to {aggregated_filename}.")
    except FileNotFoundError:
        aggregated_data = quakes
        logging.info(f"No aggregated file found. Created new {aggregated_filename}.")

    aggregated_data.to_parquet(aggregated_filename)
    logging.info(f"Aggregated data saved as {aggregated_filename}.")

except Exception as e:
    logging.error(f"Error during data processing: {e}")
    raise

logging.info("Data processing script completed successfully.")
print("Data downloaded, cleaned, and saved as parquet files.")
