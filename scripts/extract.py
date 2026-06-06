import requests
import os
import time
from datetime import datetime, timezone


def extract_weather(cities: list, retries: int = 3, backoff: float = 2.0) -> list:
    """
    Extract weather data from OpenWeatherMap API for a list of cities.
    Includes exponential backoff retry logic — if a request fails,
    it waits backoff^attempt seconds before retrying.

    Example: attempt 1 waits 2s, attempt 2 waits 4s, attempt 3 gives up.

    Args:
        cities: list of city names to fetch
        retries: number of retry attempts per city (default 3)
        backoff: base wait time in seconds between retries (default 2.0)

    Returns:
        list of raw weather records — failed cities are skipped
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    raw_data = []

    for city in cities:
        record = _fetch_with_retry(city, api_key, base_url, retries, backoff)
        if record:
            raw_data.append(record)

    print(f"Extract complete — {len(raw_data)}/{len(cities)} cities successful")
    return raw_data


def _fetch_with_retry(
    city: str,
    api_key: str,
    base_url: str,
    retries: int,
    backoff: float,
) -> dict | None:
    """
    Fetch weather for a single city with exponential backoff retry.
    Returns None if all attempts fail.
    """
    params = {"q": city, "appid": api_key, "units": "metric"}

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            print(f"✅ Extracted: {city} (attempt {attempt})")
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather_description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", None),
                "recorded_at": datetime.fromtimestamp(
                    data["dt"], tz=timezone.utc
                ),
            }

        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout fetching {city} — attempt {attempt}/{retries}")
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error for {city}: {e}")
            return None  # No point retrying HTTP errors
        except Exception as e:
            print(f"⚠️ Error fetching {city}: {e} — attempt {attempt}/{retries}")

        if attempt < retries:
            wait = backoff ** attempt
            print(f"Retrying {city} in {wait:.1f}s...")
            time.sleep(wait)

    print(f"❌ All {retries} attempts failed for {city}. Skipping.")
    return None