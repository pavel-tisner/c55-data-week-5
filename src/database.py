# Step 5 — Task 5: Database Storage
# create_tables()  — run once at startup to set up raw_weather and weather_readings.
# insert_raw()     — store every record before validation so nothing is lost.
# upsert_readings()— insert valid records; ON CONFLICT updates instead of duplicating.
# count_readings() — query the final row count for the pipeline summary.
import sqlite3
from pathlib import Path

from src.models import WeatherReading

DB_PATH = Path("weather.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create raw_weather and weather_readings tables if they do not exist.

    raw_weather columns: id, station, timestamp, temperature_c, humidity_pct, source, ingested_at
    weather_readings columns: id, station, timestamp, temperature_c, humidity_pct
        + UNIQUE(station, timestamp) constraint for upserts
    """

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT,
            timestamp TEXT,
            temperature_c TEXT,
            humidity_pct TEXT,
            source TEXT NOT NULL,
            ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            humidity_pct INTEGER NOT NULL,
            UNIQUE(station, timestamp)
        )
        """
    )

    conn.commit()


def insert_raw(conn: sqlite3.Connection, records: list[dict], source: str) -> None:
    """Insert raw records (before validation) into raw_weather.

    Use parameterized queries with placeholder syntax; do not build SQL via string formatting.
    """

    rows = [
        (
            record.get("station"),
            record.get("timestamp"),
            record.get("temperature_c"),
            record.get("humidity_pct"),
            source,
        )
        for record in records
    ]

    conn.executemany(
        """
        INSERT INTO raw_weather (
            station,
            timestamp,
            temperature_c,
            humidity_pct,
            source
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()


def upsert_readings(conn: sqlite3.Connection, readings: list[WeatherReading]) -> None:
    """Upsert valid WeatherReading objects into weather_readings.

    Use the upsert pattern to handle duplicate (station, timestamp) pairs.
    Use parameterized queries.
    """

    rows = [
        (
            reading.station,
            reading.timestamp,
            reading.temperature_c,
            reading.humidity_pct,
        )
        for reading in readings
    ]

    conn.executemany(
        """
        INSERT INTO weather_readings (
            station,
            timestamp,
            temperature_c,
            humidity_pct
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(station, timestamp)
        DO UPDATE SET
            temperature_c = excluded.temperature_c,
            humidity_pct = excluded.humidity_pct
        """,
        rows,
    )

    conn.commit()


def count_readings(conn: sqlite3.Connection) -> int:
    """Return the total number of rows in weather_readings."""

    cursor = conn.execute("SELECT COUNT(*) FROM weather_readings")
    result = cursor.fetchone()

    return result[0]
