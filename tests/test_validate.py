"""
Unit tests for the Weather ETL Pipeline data quality validator.

Each check is tested independently with a small in-memory DataFrame —
no Airflow, no database, no API calls. validate_weather() itself is
tested with both a fully valid DataFrame and DataFrames that violate
each rule, confirming the aggregated pass/fail result and that every
problem is collected, not just the first one found.
"""
import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from validate import (
    check_not_empty,
    check_required_columns,
    check_no_nulls,
    check_temperature_range,
    check_humidity_range,
    check_pressure_range,
    check_no_duplicate_city_timestamp,
    validate_weather,
)


@pytest.fixture
def valid_df():
    return pd.DataFrame([
        {
            "city": "Paris",
            "temperature": 18.5,
            "feels_like": 17.8,
            "humidity": 60,
            "pressure": 1013,
            "recorded_at": "2026-06-20T14:00:00",
        },
        {
            "city": "London",
            "temperature": 15.0,
            "feels_like": 14.2,
            "humidity": 70,
            "pressure": 1008,
            "recorded_at": "2026-06-20T14:00:00",
        },
    ])


# ── check_not_empty ─────────────────────────────────────────────────

def test_check_not_empty_passes_on_valid_df(valid_df):
    assert check_not_empty(valid_df) == []


def test_check_not_empty_fails_on_empty_df():
    problems = check_not_empty(pd.DataFrame())
    assert len(problems) == 1
    assert "empty" in problems[0].lower()


# ── check_required_columns ──────────────────────────────────────────

def test_check_required_columns_passes_on_valid_df(valid_df):
    assert check_required_columns(valid_df) == []


def test_check_required_columns_fails_when_column_missing(valid_df):
    df = valid_df.drop(columns=["humidity"])
    problems = check_required_columns(df)
    assert len(problems) == 1
    assert "humidity" in problems[0]


# ── check_no_nulls ───────────────────────────────────────────────────

def test_check_no_nulls_passes_on_valid_df(valid_df):
    assert check_no_nulls(valid_df) == []


def test_check_no_nulls_fails_when_temperature_is_null(valid_df):
    df = valid_df.copy()
    df.loc[0, "temperature"] = None
    problems = check_no_nulls(df)
    assert len(problems) == 1
    assert "temperature" in problems[0]


# ── check_temperature_range ─────────────────────────────────────────

def test_check_temperature_range_passes_on_valid_df(valid_df):
    assert check_temperature_range(valid_df) == []


def test_check_temperature_range_fails_on_impossible_value(valid_df):
    df = valid_df.copy()
    df.loc[0, "temperature"] = 200.0
    problems = check_temperature_range(df)
    assert len(problems) == 1
    assert "Paris" in problems[0]


# ── check_humidity_range ────────────────────────────────────────────

def test_check_humidity_range_passes_on_valid_df(valid_df):
    assert check_humidity_range(valid_df) == []


def test_check_humidity_range_fails_above_100(valid_df):
    df = valid_df.copy()
    df.loc[0, "humidity"] = 150
    problems = check_humidity_range(df)
    assert len(problems) == 1
    assert "Paris" in problems[0]


# ── check_pressure_range ────────────────────────────────────────────

def test_check_pressure_range_passes_on_valid_df(valid_df):
    assert check_pressure_range(valid_df) == []


def test_check_pressure_range_fails_below_minimum(valid_df):
    df = valid_df.copy()
    df.loc[0, "pressure"] = 500
    problems = check_pressure_range(df)
    assert len(problems) == 1
    assert "Paris" in problems[0]


# ── check_no_duplicate_city_timestamp ───────────────────────────────

def test_check_no_duplicates_passes_on_valid_df(valid_df):
    assert check_no_duplicate_city_timestamp(valid_df) == []


def test_check_no_duplicates_fails_on_repeated_pair(valid_df):
    df = pd.concat([valid_df, valid_df.iloc[[0]]], ignore_index=True)
    problems = check_no_duplicate_city_timestamp(df)
    assert len(problems) == 1
    assert "1 duplicate" in problems[0]


# ── validate_weather (aggregated) ───────────────────────────────────

def test_validate_weather_passes_on_fully_valid_df(valid_df):
    passed, problems = validate_weather(valid_df)
    assert passed is True
    assert problems == []


def test_validate_weather_fails_and_collects_all_problems(valid_df):
    """
    A DataFrame violating two different rules at once must report
    both problems, not stop after the first one found — a single
    DAG run should surface every issue, not just one at a time.
    """
    df = valid_df.copy()
    df.loc[0, "temperature"] = 200.0
    df.loc[1, "humidity"] = 150

    passed, problems = validate_weather(df)

    assert passed is False
    assert len(problems) == 2


def test_validate_weather_fails_on_empty_dataframe():
    passed, problems = validate_weather(pd.DataFrame())
    assert passed is False
    assert len(problems) >= 1