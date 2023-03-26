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
  station_id integer,
  time timestamp,
  available_spaces smallint
);
CREATE INDEX IF NOT EXISTS "bike_index" ON "bike_history" (station_id, time);

/* Weather history */
CREATE TABLE IF NOT EXISTS "weather_history" (
  station_id integer,
  time timestamp,
  temperature real,
  apparent_temperature real,
  relative_humidity smallint,
  dewpoint real,
  precipitation_probability smallint,
  precipitation real,
  rain real,
  showers real,
  weather_code smallint,
  pressure real,
  surface_pressure real,
  cloud_cover smallint,
  visibility real,
  evapotranspiration real,
  et0_fao_evapotranspiration real,
  vapor_pressure_deficit real,
  wind_speed real,
  wind_gusts real,
  soil_temperature real,
  soil_moisture real,
  uv_index real,
  uv_index_clear_sky real,
  cape real,
  freezinglevel_height real,
  pm2_5 real,
  pm10 real,
  carbon_monoxide real,
  nitrogen_dioxide real,
  sulphur_dioxide real,
  ozone real,
  aerosol_optical_depth real,
  dust real,
  us_aqi smallint,
  us_aqi_pm2_5 smallint,
  us_aqi_pm10 smallint,
  us_aqi_no2 smallint,
  us_aqi_co smallint,
  us_aqi_o3 smallint,
  us_aqi_so2 smallint
);
CREATE INDEX IF NOT EXISTS "weather_index" ON "weather_history" (station_id, time);
