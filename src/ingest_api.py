# Step 2 — Tasks 1 & 2: Error Handling + API Ingestion
# fetch_with_retry handles transient network errors (Task 1).
# fetch_api_records calls it and shapes the response into flat dicts (Task 2).
import logging
import time

import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_with_retry(
    url: str, params: dict, max_retries: int = 3, timeout: int = 10
) -> dict:
    """Fetch url with exponential backoff on transient errors.

    Retry on: ConnectionError, Timeout, 5xx status codes.
    Fail immediately on: 4xx status codes.
    Log each retry attempt with the error and delay.
    """
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            if 400 <= response.status_code < 500:
                response.raise_for_status()

            if 500 <= response.status_code < 600:
                raise requests.exceptions.HTTPError(
                    f"Server error {response.status_code}",
                    response=response,
                )

            response.raise_for_status()
            return response.json()

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as error:
            if attempt == max_retries:
                logger.error("Request failed after %s retries: %s", max_retries, error)
                raise

            delay = 2**attempt
            logger.warning(
                "Transient network error on attempt %s/%s: %s. Retrying in %s seconds.",
                attempt + 1,
                max_retries + 1,
                error,
                delay,
            )
            time.sleep(delay)

        except requests.exceptions.HTTPError as error:
            status_code = None

            if error.response is not None:
                status_code = error.response.status_code

            if status_code is not None and 500 <= status_code < 600:
                if attempt == max_retries:
                    logger.error(
                        "Server error after %s retries: %s", max_retries, error
                    )
                    raise

                delay = 2**attempt
                logger.warning(
                    "Server error on attempt %s/%s: %s. Retrying in %s seconds.",
                    attempt + 1,
                    max_retries + 1,
                    error,
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error("Permanent HTTP error, not retrying: %s", error)
                raise

    raise RuntimeError("fetch_with_retry exited unexpectedly")


def fetch_api_records() -> list[dict]:
    """Fetch hourly weather from Open-Meteo and return flat dicts.

    Returns a list of dicts with keys: station, timestamp, temperature_c, humidity_pct.
    Returns [] if the API returns no data (do not raise an exception).
    """
    params = {
        "latitude": 55.67,
        "longitude": 12.56,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 7,
    }
    data = fetch_with_retry(API_URL, params=params)

    hourly = data.get("hourly")

    if not hourly:
        return []

    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])

    if not times or not temperatures or not humidities:
        return []

    records = []

    for index in range(min(len(times), len(temperatures), len(humidities))):
        record = {
            "station": "Open-Meteo Copenhagen",
            "timestamp": times[index],
            "temperature_c": temperatures[index],
            "humidity_pct": humidities[index],
        }

        records.append(record)

    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    api_records = fetch_api_records()
