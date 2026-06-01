# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-05-12

### Added
- Airflow 2.8.1 DAG orchestrating hourly ETL for 5 cities across 4 continents
- Extract module hitting OpenWeatherMap REST API
- Transform module with Pandas — null handling, type validation, derived temp_category column
- Idempotent load module with deduplication on (city, recorded_at)
- PostgreSQL 13 storage with indexed schema
- Docker Compose stack with Airflow webserver, scheduler and PostgreSQL
- 20 pytest unit tests covering all transform and load logic
- GitHub Actions CI pipeline
- Makefile with shortcuts for up, down, logs, test and clean
- Mermaid architecture diagram in README
- Sample output table in README

## [1.0.1] - 2026-06-01

### Improved
- Added project roadmap: next steps include DuckDB analytics integration and cloud deployment on AWS
