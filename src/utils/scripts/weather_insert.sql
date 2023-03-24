INSERT INTO "weather_history" (
  station_id, time, temperature, weather_code,
  wind_speed, wind_degree, pressure,
  precipitation, humidity, cloudiness,
  feels_like, visibility, uv_index,
  wind_gust, is_day, co, no2, o3, so2,
  pm2_5, pm10, us_epa_index, gb_defra_index
)
VALUES
  (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
    $11, $12, $13, $14, $15, $16, $17, $18,
    $19, $20, $21, $22, $23
  )
