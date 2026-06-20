"""
Data quality validation for transformed weather data.

Runs a series of checks against the transformed DataFrame before it
reaches load(). Each check returns a list of problems found — an
empty list means the check passed. The DAG fails the run if any
check fails, preventing bad data from ever reaching PostgreSQL.

This mirrors the same quality-checking pattern used in the DuckDB
analytics project, applied here at ingestion time instead of at
the analytical layer.
"""
import pandas as pd

# Plausible ranges for OpenWeatherMap fields — used to catch
# upstream API errors or transformation bugs before they reach the DB.
TEMPERATURE_RANGE = (-80, 60)
HUMIDITY_RANGE = (0, 100)
PRESSURE_RANGE = (800, 1100)
REQUIRED_COLUMNS = [
    "city", "temperature", "feels_like", "humidity",
    "pressure", "recorded_at",
]


def check_not_empty(df: pd.DataFrame) -> list[str]:
    """The DataFrame must contain at least one row."""
    if df.empty:
        return ["DataFrame is empty — no records to load."]
    return []


def check_required_columns(df: pd.DataFrame) -> list[str]:
    """Every required column must be present."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return [f"Missing required columns: {missing}"]
    return []


def check_no_nulls(df: pd.DataFrame) -> list[str]:
    """No required column may contain null values after transformation."""
    problems = []
    for col in REQUIRED_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            count = df[col].isnull().sum()
            problems.append(f"Column '{col}' has {count} null value(s).")
    return problems


def check_temperature_range(df: pd.DataFrame) -> list[str]:
    """Temperature must fall within a physically plausible range."""
    if "temperature" not in df.columns:
        return []
    out_of_range = df[
        (df["temperature"] < TEMPERATURE_RANGE[0])
        | (df["temperature"] > TEMPERATURE_RANGE[1])
    ]
    if not out_of_range.empty:
        cities = out_of_range["city"].tolist()
        return [
            f"{len(out_of_range)} record(s) outside temperature range "
            f"{TEMPERATURE_RANGE} for cities: {cities}"
        ]
    return []


def check_humidity_range(df: pd.DataFrame) -> list[str]:
    """Humidity must be a valid percentage."""
    if "humidity" not in df.columns:
        return []
    out_of_range = df[
        (df["humidity"] < HUMIDITY_RANGE[0])
        | (df["humidity"] > HUMIDITY_RANGE[1])
    ]
    if not out_of_range.empty:
        cities = out_of_range["city"].tolist()
        return [
            f"{len(out_of_range)} record(s) outside humidity range "
            f"{HUMIDITY_RANGE} for cities: {cities}"
        ]
    return []


def check_pressure_range(df: pd.DataFrame) -> list[str]:
    """Atmospheric pressure must fall within a plausible range."""
    if "pressure" not in df.columns:
        return []
    out_of_range = df[
        (df["pressure"] < PRESSURE_RANGE[0])
        | (df["pressure"] > PRESSURE_RANGE[1])
    ]
    if not out_of_range.empty:
        cities = out_of_range["city"].tolist()
        return [
            f"{len(out_of_range)} record(s) outside pressure range "
            f"{PRESSURE_RANGE} for cities: {cities}"
        ]
    return []


def check_no_duplicate_city_timestamp(df: pd.DataFrame) -> list[str]:
    """
    No city should appear more than once for the same recorded_at
    timestamp — transform_weather() already deduplicates, this check
    catches a regression if that logic is ever changed.
    """
    if "city" not in df.columns or "recorded_at" not in df.columns:
        return []
    duplicates = df.duplicated(subset=["city", "recorded_at"])
    if duplicates.any():
        count = duplicates.sum()
        return [f"{count} duplicate (city, recorded_at) pair(s) found."]
    return []


CHECKS = [
    check_not_empty,
    check_required_columns,
    check_no_nulls,
    check_temperature_range,
    check_humidity_range,
    check_pressure_range,
    check_no_duplicate_city_timestamp,
]


def validate_weather(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Runs all quality checks against the transformed DataFrame.

    Returns (passed, problems) — passed is False if any check found
    a problem, and problems is the full list of issues found across
    every check, not just the first one. Running every check even
    after an early failure means a single DAG run surfaces all data
    quality issues at once, rather than requiring multiple runs to
    discover them one at a time.
    """
    all_problems = []
    for check in CHECKS:
        all_problems.extend(check(df))

    passed = len(all_problems) == 0
    if passed:
        print(f"✅ Data quality validation passed — {len(df)} records checked.")
    else:
        print(f"❌ Data quality validation failed — {len(all_problems)} issue(s) found:")
        for problem in all_problems:
            print(f"   - {problem}")

    return passed, all_problems