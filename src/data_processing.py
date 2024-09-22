import logging
import sys
import requests
import pandas as pd
from datetime import datetime, timezone
from requests.exceptions import RequestException

# Set up logging (file + console)
log_file = "data_processing.log"
logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Constants for directories and URLs
DATA_DIR = "../data"
EARTHQUAKE_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
)


def fetch_earthquake_data() -> pd.DataFrame:
    """Fetch and return earthquake data as a pandas DataFrame."""
    try:
        response = requests.get(EARTHQUAKE_URL)
        response.raise_for_status()
        jsondata = response.json()
        quakes = pd.json_normalize(jsondata["features"])

        # Clean up and organize the data
        quakes.columns = quakes.columns.str.replace("properties.", "", regex=False)
        quakes.columns = quakes.columns.str.replace("geometry.", "", regex=False)

        quakes = clean_quake_data(quakes)
        logging.info("Data downloaded and cleaned successfully.")
        return quakes
    except RequestException as req_err:
        logging.error(f"Error fetching earthquake data: {req_err}")
        raise


def clean_quake_data(quakes: pd.DataFrame) -> pd.DataFrame:
    """Clean the earthquake data and return the DataFrame."""
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

    quakes["longitude"] = quakes["coordinates"].str[0]
    quakes["latitude"] = quakes["coordinates"].str[1]
    quakes["depth"] = quakes["coordinates"].str[2]
    quakes.drop(columns=["coordinates"], inplace=True)

    quakes["tsunami_warning"] = quakes["tsunami"].astype(bool)
    quakes.drop(columns=["tsunami"], inplace=True)

    return quakes


def save_quake_data(quakes: pd.DataFrame) -> None:
    """Save the quake data as daily and aggregated parquet files."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_filename = f"{DATA_DIR}/quakes_{today}.parquet"

    quakes.to_parquet(daily_filename)
    logging.info(f"Today's data saved as {daily_filename}.")

    aggregated_filename = f"{DATA_DIR}/aggregated_data.parquet"
    try:
        aggregated_data = pd.read_parquet(aggregated_filename)
        aggregated_data = pd.concat([aggregated_data, quakes], ignore_index=True)
        logging.info(f"Appended today's data to {aggregated_filename}.")
    except FileNotFoundError:
        aggregated_data = quakes
        logging.info(f"No aggregated file found. Created new {aggregated_filename}.")

    aggregated_data.to_parquet(aggregated_filename)
    logging.info(f"Aggregated data saved as {aggregated_filename}.")


def main():
    logging.info("Data processing script started.")

    try:
        quakes = fetch_earthquake_data()
        save_quake_data(quakes)
    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

    logging.info("Data processing script completed successfully.")
    print("Data downloaded, cleaned, and saved as parquet files.")


if __name__ == "__main__":
    main()
