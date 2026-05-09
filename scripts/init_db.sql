-- Create weather user
CREATE USER weather_user WITH PASSWORD 'weather_pass';

-- Create weather database
CREATE DATABASE weather_db OWNER weather_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE weather_db TO weather_user;

-- Connect to weather_db and create table
\c weather_db;

CREATE TABLE IF NOT EXISTS weather_data (
    id                  SERIAL PRIMARY KEY,
    city                VARCHAR(100) NOT NULL,
    country             VARCHAR(10),
    temperature         FLOAT,
    feels_like          FLOAT,
    humidity            INTEGER,
    pressure            INTEGER,
    weather_description VARCHAR(255),
    wind_speed          FLOAT,
    visibility          INTEGER,
    recorded_at         TIMESTAMP NOT NULL,
    inserted_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weather_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weather_user;

CREATE INDEX idx_weather_city ON weather_data(city);
CREATE INDEX idx_weather_recorded_at ON weather_data(recorded_at);