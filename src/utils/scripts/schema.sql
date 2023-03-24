/* Station list */
CREATE TABLE IF NOT EXISTS "station_list" (
  station_id integer UNIQUE,
  location geometry(Point),
  area_code text,
  bike_type smallint,
  total_spaces smallint
);
CREATE UNIQUE INDEX IF NOT EXISTS "station_id" ON "station_list" (station_id);

/* Bike history */
CREATE TABLE IF NOT EXISTS "bike_history" (
  station_id integer, time timestamp,
  available_spaces smallint
);
CREATE INDEX IF NOT EXISTS "bike_index" ON "bike_history" (station_id, time);

/* Weather history */
CREATE TABLE IF NOT EXISTS "weather_history" (
  station_id integer, time timestamp,
  temperature real, weather_code smallint,
  wind_speed real, wind_degree smallint,
  pressure real, precipitation real,
  humidity int, cloudiness int, feels_like real,
  visibility real, uv_index real, wind_gust real,
  is_day smallint, co real, no2 real,
  o3 real, so2 real, pm2_5 real, pm10 real,
  us_epa_index smallint, gb_defra_index smallint
);
CREATE INDEX IF NOT EXISTS "weather_index" ON "weather_history" (station_id, time);
