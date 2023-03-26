INSERT INTO "weather_history" (
  station_id, time, temperature, apparent_temperature,
  relative_humidity, dewpoint, precipitation_probability,
  precipitation, rain, showers, weather_code,
  pressure, surface_pressure, cloud_cover,
  visibility, evapotranspiration,
  et0_fao_evapotranspiration, vapor_pressure_deficit,
  wind_speed, wind_gusts, soil_temperature,
  soil_moisture, uv_index, uv_index_clear_sky,
  cape, freezinglevel_height, pm2_5,
  pm10, carbon_monoxide, nitrogen_dioxide,
  sulphur_dioxide, ozone, aerosol_optical_depth,
  dust, us_aqi, us_aqi_pm2_5, us_aqi_pm10,
  us_aqi_no2, us_aqi_co, us_aqi_o3,
  us_aqi_so2
)
VALUES
  (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
    $11, $12, $13, $14, $15, $16, $17, $18,
    $19, $20, $21, $22, $23, $24, $25, $26,
    $27, $28, $29, $30, $31, $32, $33, $34,
    $35, $36, $37, $38, $39, $40, $41
  )
