import os
import pandas as pd
from sqlalchemy import create_engine, text


def get_engine():
    """Create and return a SQLAlchemy engine for weather_db."""
    user = os.getenv("WEATHER_DB_USER", "weather_user")
    password = os.getenv("WEATHER_DB_PASSWORD", "weather_pass")
    db = os.getenv("WEATHER_DB_NAME", "weather_db")
    host = "postgres"
    port = 5432

    conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(conn_string)
    return engine


def load_weather(df: pd.DataFrame) -> None:
    """
    Load transformed weather data into PostgreSQL.
    Skips duplicates based on city + recorded_at.
    """
    if df.empty:
        print("⚠️ No data to load.")
        return

    engine = get_engine()

    # Drop the derived column before loading — not in DB schema
    df = df.drop(columns=["temp_category"], errors="ignore")

    records_loaded = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            # Check for existing record to avoid duplicates
            check = text("""
                SELECT 1 FROM weather_data
                WHERE city = :city AND recorded_at = :recorded_at
            """)
            exists = conn.execute(check, {
                "city": row["city"],
                "recorded_at": row["recorded_at"]
            }).fetchone()

            if not exists:
                insert = text("""
                    INSERT INTO weather_data (
                        city, country, temperature, feels_like,
                        humidity, pressure, weather_description,
                        wind_speed, visibility, recorded_at
                    ) VALUES (
                        :city, :country, :temperature, :feels_like,
                        :humidity, :pressure, :weather_description,
                        :wind_speed, :visibility, :recorded_at
                    )
                """)
                conn.execute(insert, row.to_dict())
                records_loaded += 1

    print(f"✅ Loaded {records_loaded} new records into PostgreSQL.")