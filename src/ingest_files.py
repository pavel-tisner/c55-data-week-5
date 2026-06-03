# Step 3 — Task 3: File Reading
# Read the messy CSV and normalize each row into the same dict format
# that fetch_api_records() produces, so validate_records() can handle both sources.
import csv
from pathlib import Path
from typing import Union


def convert_temperature(value: str) -> Union[float, str]:
    """Convert temperature_c to float where possible."""
    try:
        return float(value)
    except ValueError:
        return value


def convert_humidity(value: str) -> Union[int, str]:
    """Convert humidity_pct to int where possible."""
    try:
        return int(value)
    except ValueError:
        return value


def read_csv_records(path: Path) -> list[dict]:
    """Read weather_stations.csv and return normalized records.

    Returns a list of dicts with keys: station, timestamp, temperature_c, humidity_pct.

    Rules:
    - Open with newline="" and encoding="utf-8".
    - Use csv.DictReader.
    - Convert temperature_c to float and humidity_pct to int where possible.
    - Leave unconvertible values (e.g. "N/A", "") as-is so validation can catch them.
    """
    records = []

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            record = {
                "station": row["station"],
                "timestamp": row["timestamp"],
                "temperature_c": convert_temperature(row["temperature_c"]),
                "humidity_pct": convert_humidity(row["humidity_pct"]),
            }

            records.append(record)

    return records


if __name__ == "__main__":
    csv_path = Path("data/weather_stations.csv")
    records = read_csv_records(csv_path)
