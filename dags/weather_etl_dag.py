from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow/scripts')

from extract import extract_weather
from transform import transform_weather
from load import load_weather

# Cities to track
CITIES = [
    "Paris",
    "London",
    "New York",
    "Tokyo",
    "Douala"
]

default_args = {
    "owner": "ojong",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_extract(**context):
    raw_data = extract_weather(CITIES)
    context["ti"].xcom_push(key="raw_data", value=raw_data)
    print(f"✅ Extracted {len(raw_data)} records.")


def run_transform(**context):
    raw_data = context["ti"].xcom_pull(key="raw_data", task_ids="extract")
    df = transform_weather(raw_data)
    records = df.to_dict(orient="records")
    context["ti"].xcom_push(key="transformed_data", value=records)
    print(f"✅ Transformed {len(records)} records.")


def run_load(**context):
    import pandas as pd
    records = context["ti"].xcom_pull(key="transformed_data", task_ids="transform")
    df = pd.DataFrame(records)
    load_weather(df)
    print(f"✅ Load complete.")


with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    description="ETL pipeline for weather data using OpenWeatherMap API",
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["weather", "etl", "data-engineering"],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=run_extract,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=run_transform,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=run_load,
    )

    extract >> transform >> load