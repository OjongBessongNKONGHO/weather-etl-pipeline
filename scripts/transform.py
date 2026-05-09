import pandas as pd


def transform_weather(raw_data: list) -> pd.DataFrame:
    """
    Transform raw weather data into a clean DataFrame.
    - Removes duplicates
    - Handles missing values
    - Validates data types
    - Adds derived columns
    """
    if not raw_data:
        print("⚠️ No data to transform.")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    # Drop duplicates
    df = df.drop_duplicates(subset=["city", "recorded_at"])

    # Drop rows where critical fields are missing
    df = df.dropna(subset=["city", "temperature", "recorded_at"])

    # Fill optional missing values
    df["visibility"] = df["visibility"].fillna(0).astype(int)
    df["wind_speed"] = df["wind_speed"].fillna(0.0)

    # Ensure correct data types
    df["temperature"] = df["temperature"].astype(float)
    df["feels_like"] = df["feels_like"].astype(float)
    df["humidity"] = df["humidity"].astype(int)
    df["pressure"] = df["pressure"].astype(int)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    # Add a derived column: temperature category
    df["temp_category"] = df["temperature"].apply(categorize_temperature)

    print(f"✅ Transformed {len(df)} records successfully.")
    return df


def categorize_temperature(temp: float) -> str:
    """Categorize temperature into human-readable labels."""
    if temp < 0:
        return "freezing"
    elif temp < 10:
        return "cold"
    elif temp < 20:
        return "mild"
    elif temp < 30:
        return "warm"
    else:
        return "hot"