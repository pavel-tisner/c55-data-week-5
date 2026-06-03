"""
Week 5 assignment: containerised data pipeline.

Tasks:
- Task 1: confirm this script runs locally before touching the Dockerfile.
- Task 5: read all configuration from environment variables (no hardcoded values).

This file contains the Week 3 pipeline adapted for the Week 5 container assignment.
"""

import json
import logging
import os
from pathlib import Path

from src.database import (
    count_readings,
    create_tables,
    get_connection,
    insert_raw,
    upsert_readings,
)
from src.ingest_api import fetch_api_records
from src.ingest_files import read_csv_records
from src.validate import validate_records

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_config() -> dict:
    """
    Return configuration read from environment variables.

    Required variable: API_KEY
    Optional variable: OUTPUT_DIR (default "output")

    Raise RuntimeError with a clear message if a required variable is missing.
    """
    api_key = os.environ.get("API_KEY")

    if not api_key:
        raise RuntimeError("Missing required environment variable: API_KEY")

    return {
        "api_key": api_key,
        "output_dir": os.environ.get("OUTPUT_DIR", "output"),
        "csv_path": os.environ.get("CSV_PATH", "data/weather_stations.csv"),
    }


def run_pipeline() -> None:
    config = get_config()

    output_dir = Path(config["output_dir"])
    csv_path = Path(config["csv_path"])

    output_dir.mkdir(exist_ok=True)

    logger.info("starting pipeline")

    api_records = fetch_api_records()
    csv_records = read_csv_records(csv_path)

    conn = get_connection()
    create_tables(conn)

    insert_raw(conn, api_records, source="api")
    insert_raw(conn, csv_records, source="csv")

    all_records = api_records + csv_records

    valid_records, error_records = validate_records(
        all_records,
        source="api+csv",
    )

    upsert_readings(conn, valid_records)

    error_report_path = output_dir / "error_report.json"

    with error_report_path.open("w", encoding="utf-8") as file:
        json.dump(error_records, file, indent=2, ensure_ascii=False)

    records_in_database = count_readings(conn)

    logger.info("API records fetched: %s", len(api_records))
    logger.info("CSV records read: %s", len(csv_records))
    logger.info("Total raw records: %s", len(all_records))
    logger.info("Valid records: %s", len(valid_records))
    logger.info("Invalid records: %s", len(error_records))
    logger.info("Records in database: %s", records_in_database)
    logger.info("Error report: %s", error_report_path)
    logger.info("pipeline complete")

    conn.close()


def run() -> None:
    run_pipeline()


if __name__ == "__main__":
    run()
