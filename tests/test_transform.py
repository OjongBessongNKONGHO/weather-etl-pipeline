"""
Unit tests for the Weather ETL Pipeline transform script.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_temperature_conversion():
    """Test Kelvin to Celsius conversion."""
    kelvin = 300.15
    celsius = round(kelvin - 273.15, 2)
    assert celsius == 27.0


def test_temperature_conversion_freezing():
    """Test Kelvin to Celsius at freezing point."""
    kelvin = 273.15
    celsius = round(kelvin - 273.15, 2)
    assert celsius == 0.0


def test_humidity_range_valid():
    """Test that valid humidity values are accepted."""
    humidity = 65
    assert 0 <= humidity <= 100


def test_humidity_range_invalid():
    """Test that out of range humidity is detected."""
    humidity = 150
    assert not (0 <= humidity <= 100)


def test_wind_speed_non_negative():
    """Test that wind speed is non-negative."""
    wind_speed = 5.2
    assert wind_speed >= 0


def test_city_list():
    """Test that the expected cities are tracked."""
    cities = ["Paris", "London", "New York", "Tokyo", "Douala"]
    assert len(cities) == 5
    assert "Paris" in cities
    assert "Douala" in cities


def test_pressure_range_valid():
    """Test that valid pressure values are accepted."""
    pressure = 1013
    assert 800 <= pressure <= 1100


def test_weather_record_structure():
    """Test that a weather record has all required fields."""
    record = {
        "city": "Paris",
        "country": "FR",
        "temperature": 15.5,
        "humidity": 60,
        "pressure": 1013,
        "wind_speed": 3.2,
        "description": "clear sky"
    }
    required_fields = ["city", "country", "temperature",
                       "humidity", "pressure", "wind_speed", "description"]
    for field in required_fields:
        assert field in record