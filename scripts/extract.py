import requests
import os
from datetime import datetime


def extract_weather(cities: list) -> list:
    """
    Extract weather data from OpenWeatherMap API for a list of cities.
    Returns a list of raw weather records.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    raw_data = []

    for city in cities:
        try:
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric"
            }
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            raw_data.append({
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather_description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", None),
                "recorded_at": datetime.utcfromtimestamp(data["dt"])
            })

            print(f"✅ Extracted: {city}")

        except Exception as e:
            print(f"❌ Failed to extract {city}: {e}")

    return raw_data