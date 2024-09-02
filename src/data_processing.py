import requests
import pandas as pd
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Replace pytz for timezone handling
import os
from pathlib import Path
from requests.exceptions import RequestException

# Define the timezone
eastern = ZoneInfo("US/Eastern")

# Get the top-level directory (parent of src) using Pathlib for better handling
top_level_dir = Path(__file__).resolve().parent.parent

# Set up log and data directories at the top level
log_dir = top_level_dir / "logs"
data_dir = top_level_dir / "data"

log_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)

# Set up logging with better log rotation handling
from logging.handlers import TimedRotatingFileHandler

log_file = log_dir / "data_processing.log"
handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Data processing script started.")

try:
    # Fetch earthquake data
    response = requests.get(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    )
    response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
    jsondata = response.json()

    quakes = pd.json_normalize(jsondata["features"])

    # Clean up column names and remove unnecessary columns
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
            "types",
            "nst",
            "title",
        ],
        axis=1,
        inplace=True,
    )

    quakes["ids"] = quakes["ids"].str.strip(",")
    quakes["sources"] = quakes["sources"].str.strip(",")

    quakes["datetime"] = pd.to_datetime(quakes["time"], unit="ms", utc=True)
    quakes.drop(columns=["time"], inplace=True)

    # Extract coordinates
    quakes["longitude"] = quakes.coordinates.str[0]
    quakes["latitude"] = quakes.coordinates.str[1]
    quakes["depth"] = quakes.coordinates.str[2]
    quakes.drop(columns=["coordinates"], inplace=True)

    # Handle tsunami warnings as a boolean column
    quakes["tsunami_warning"] = quakes["tsunami"].astype("bool")
    quakes.drop(columns=["tsunami"], inplace=True)

    logging.info("Data downloaded and cleaned successfully.")

    # Save the cleaned data to parquet
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_filename = data_dir / f"quakes_{today}.parquet"
    quakes.to_parquet(daily_filename)
    logging.info(f"Today's data saved as {daily_filename}.")

    aggregated_filename = data_dir / "aggregated_data.parquet"
    try:
        aggregated_data = pd.read_parquet(aggregated_filename)
        aggregated_data = pd.concat([aggregated_data, quakes], ignore_index=True)
        logging.info(f"Appended today's data to {aggregated_filename}.")
    except FileNotFoundError:
        aggregated_data = quakes
        logging.info(f"No aggregated file found. Created new {aggregated_filename}.")

    aggregated_data.to_parquet(aggregated_filename)
    logging.info(f"Aggregated data saved as {aggregated_filename}.")

except RequestException as req_err:
    logging.error(f"HTTP request error during data processing: {req_err}")
    raise
except pd.errors.EmptyDataError as pd_err:
    logging.error(f"Pandas encountered an empty data error: {pd_err}")
    raise
except Exception as e:
    logging.error(f"Unexpected error during data processing: {e}")
    raise

logging.info("Data processing script completed successfully.")
print("Data downloaded, cleaned, and saved as parquet files.")
