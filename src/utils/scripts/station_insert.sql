INSERT INTO "station_list" (
  station_id, location, area_code, bike_type,
  total_spaces
)
VALUES
  (
    $1,
    ST_SetSRID(
      ST_MakePoint($2, $3),
      4326
    ),
    $4,
    $5,
    $6
  ) ON CONFLICT (station_id) DO
UPDATE
SET
  total_spaces = EXCLUDED.total_spaces;
