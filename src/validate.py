# Step 4 — Task 4: Pydantic Validation (batch)
# validate_records() runs every record through WeatherReading and splits the
# results into a valid list and an error list. pipeline.py calls this once for
# all records combined, then stores the valid ones and saves the errors to JSON.
from pydantic import ValidationError

from src.models import WeatherReading


def validate_records(
    records: list[dict], source: str
) -> tuple[list[WeatherReading], list[dict]]:
    """Validate records against WeatherReading and return (valid_list, error_list).

    Each error dict must contain:
        index       - position of the record in the input list
        source      - the source string passed in (e.g. "api" or "csv")
        raw_record  - the original dict
        error_details - the Pydantic error list (ValidationError.errors())
    """
    valid_list = []
    error_list = []

    for index, record in enumerate(records):
        try:
            validated_record = WeatherReading(**record)
            valid_list.append(validated_record)
        except ValidationError as error:
            error_list.append(
                {
                    "index": index,
                    "source": source,
                    "raw_record": record,
                    "error_details": error.errors(),
                }
            )

    return valid_list, error_list


if __name__ == "__main__":
    from pathlib import Path

    from src.ingest_files import read_csv_records

    csv_records = read_csv_records(Path("data/weather_stations.csv"))

    valid, errors = validate_records(csv_records, source="csv")
