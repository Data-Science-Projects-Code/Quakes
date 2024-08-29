import requests
import pandas as pd
import logging
from datetime import datetime
import os

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
logging.basicConfig(
    filename=os.path.join(
        log_dir, f'data_processing_{datetime.utcnow().strftime("%Y-%m-%d")}.log'
    ),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Data processing script started.")


# Fetch, clean, and save data as parquet; log results
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
    daily_filename = f"data/quakes_{today}.parquet"
    os.makedirs("data", exist_ok=True)  # Create the data directory if it doesn't exist
    quakes.to_parquet(daily_filename)
    logging.info(f"Today's data saved as {daily_filename}.")

    # Step 4: Append today's data to the aggregated Parquet file
    aggregated_filename = "data/aggregated_data.parquet"
    try:
        aggregated_data = pd.read_parquet(aggregated_filename)
        aggregated_data = pd.concat([aggregated_data, quakes], ignore_index=True)
        logging.info(f"Appended today's data to {aggregated_filename}.")
    except FileNotFoundError:
        aggregated_data = quakes  # If no aggregated file exists, start fresh
        logging.info(f"No aggregated file found. Created new {aggregated_filename}.")

    aggregated_data.to_parquet(aggregated_filename)
    logging.info(f"Aggregated data saved as {aggregated_filename}.")

except Exception as e:
    logging.error(f"Error during data processing: {e}")
    raise

logging.info("Data processing script completed successfully.")
print("Data downloaded, cleaned, and saved as parquet files.")
