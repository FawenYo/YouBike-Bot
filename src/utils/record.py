import asyncio
import os
from datetime import datetime
from typing import Dict, List

import aiohttp
import asyncpg
from loguru import logger

import config


class Record:
    def __init__(self, bike_type):
        self.conn = None
        self.bike_type = bike_type
        self.data: Dict[tuple] = []
        self.weather_info = {}

    async def start(self):
        self.conn = await asyncpg.connect(config.pg_conn_info)

        await asyncio.gather(
            self.fetch_youbike_data(),
            self.fetch_weather(),
        )

        await self.update_youbike()
        await self.update_weather()
        
        await self.conn.close()

    async def fetch_youbike_data(self):
        logger.debug("Fetching YouBike data with API...")
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://apis.youbike.com.tw/api/front/station/all?lang=tw&type={self.bike_type}"
            )
            temp = await response.json()
        for each in temp["retVal"]:
            # Available station
            if each["status"] == 1:
                # Check if the station is not empty
                if each["lat"] != "" and each["lng"] != "":
                    self.data.append(each)
        logger.debug("YouBike data fetched")

    async def fetch_weather(self):
        logger.debug("Fetching weather info...")
        weather_apis: List[str] = os.getenv("WEATHER_API").split(",")

        async with aiohttp.ClientSession() as session:
            chunks = [self.data[x : x + 110] for x in range(0, len(self.data), 110)]
            for index, chunk in enumerate(chunks):
                api = weather_apis[index]
                tasks = []
                for station in chunk:
                    station_no = station["station_no"]
                    time = station["updated_at"]
                    lat = station["lat"]
                    lng = station["lng"]
                    task = asyncio.ensure_future(
                        self.fetch_weather_info(
                            session, api, station_no, time, lat, lng
                        )
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)
        logger.debug("Weather info fetched")

    async def fetch_weather_info(self, session, api, station_no, time, lat, lng):
        response = await session.get(
            f"https://api.weatherapi.com/v1/current.json?key={api}&q={lat},{lng}&aqi=yes"
        )
        json = await response.json()
        self.weather_info[station_no] = (
            int(station_no),
            time,
            float(json["current"]["temp_c"]),
            int(json["current"]["condition"]["code"]),
            float(json["current"]["wind_kph"]),
            int(json["current"]["wind_degree"]),
            float(json["current"]["pressure_mb"]),
            float(json["current"]["precip_mm"]),
            int(json["current"]["humidity"]),
            int(json["current"]["cloud"]),
            float(json["current"]["feelslike_c"]),
            float(json["current"]["vis_km"]),
            float(json["current"]["uv"]),
            float(json["current"]["gust_kph"]),
            int(json["current"]["is_day"]),
            float(json["current"]["air_quality"]["co"]),
            float(json["current"]["air_quality"]["no2"]),
            float(json["current"]["air_quality"]["o3"]),
            float(json["current"]["air_quality"]["so2"]),
            float(json["current"]["air_quality"]["pm2_5"]),
            float(json["current"]["air_quality"]["pm10"]),
            int(json["current"]["air_quality"]["us-epa-index"]),
            int(json["current"]["air_quality"]["gb-defra-index"]),
        )

    async def update_youbike(self):
        insert_commands = []
        await self.init_schema()
        db_stations = await self.fetch_database_stations()

        logger.info("Start to update bike_history table...")

        for each in self.data:
            station_no = int(each["station_no"])

            data = (
                station_no,
                datetime.strptime(each["updated_at"], "%Y-%m-%d %H:%M:%S"),
                int(each["available_spaces"]),
            )

            if str(station_no) not in db_stations:
                await self.insert_station(data=each)
            else:
                if int(each["parking_spaces"]) != db_stations[str(station_no)]:
                    await self.insert_station(data=each)
            insert_commands.append(data)

        await self.insert_bike_table(insert_commands=insert_commands)

    async def update_weather(self):
        insert_commands = []
        logger.info("Start to update weather_history table...")

        for station_no in self.weather_info:
            data = self.weather_info[station_no]

            insert_commands.append(data)

        await self.insert_weather_table(insert_commands=insert_commands)

    async def fetch_database_stations(self):
        stations = {}

        async with self.conn.transaction():
            results = await self.conn.fetch(
                'SELECT station_id, total_spaces FROM "station_list" WHERE bike_type=$1', self.bike_type
            )
            for each in results:
                stations[str(each["station_id"])] = each["total_spaces"]
        return stations

    async def insert_bike_table(
        self, insert_commands: List[tuple]
    ):
        _sql_command = f"""
        INSERT INTO "bike_history" (station_id, time, available_spaces)
        VALUES ($1, $2, $3)
        """
        async with self.conn.transaction():
            await self.conn.executemany(
                _sql_command, insert_commands
            )
        logger.info("bike_history table updated")

    async def insert_weather_table(
        self, insert_commands: List[tuple]
    ):
        _sql_command = f"""
        INSERT INTO "weather_history" (station_id, time, temperature, weather_code, wind_speed, wind_degree, pressure, precipitation, humidity, cloudiness, feels_like, visibility, uv_index, wind_gust, is_day, co, no2, o3, so2, pm2_5, pm10, us_epa_index, gb_defra_index)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)
        """
        async with self.conn.transaction():
            await self.conn.executemany(
                _sql_command, insert_commands
            )
        logger.info("weather_history table updated")

    async def init_schema(self):
        async with self.conn.transaction():
            await self.conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "station_list"
                (
                    station_id     integer UNIQUE,
                    location       geometry(Point),
                    area_code      text,
                    bike_type      smallint,
                    total_spaces   smallint
                );
                CREATE UNIQUE INDEX IF NOT EXISTS "station_id" ON "station_list" (station_id);
                
                CREATE TABLE IF NOT EXISTS "bike_history"
                (
                    station_id         integer,
                    time               timestamp,
                    available_spaces   smallint
                );
                CREATE INDEX IF NOT EXISTS "bike_index"
                    ON "bike_history" (station_id, time);
                
                CREATE TABLE IF NOT EXISTS "weather_history"
                (
                    station_id       integer,
                    time             timestamp,
                    temperature      real,
                    weather_code     smallint,
                    wind_speed       real,
                    wind_degree      smallint,
                    pressure         real,
                    precipitation    real,
                    humidity         int,
                    cloudiness       int,
                    feels_like       real,
                    visibility       real,
                    uv_index         real,
                    wind_gust        real,
                    is_day           smallint,
                    co               real,
                    no2              real,
                    o3               real,
                    so2              real,
                    pm2_5            real,
                    pm10             real,
                    us_epa_index     smallint,
                    gb_defra_index   smallint
                );
                CREATE INDEX IF NOT EXISTS "weather_index"
                    ON "weather_history" (station_id, time);
                """
            )

    async def insert_station(
        self,
        data: dict,
    ):
        async with self.conn.transaction():
            await self.conn.execute(
                f"""
            INSERT INTO "station_list" (station_id, location, area_code, bike_type, total_spaces)
            VALUES ({data['station_no']}, ST_SetSRID(ST_MakePoint({data['lat']}, {data['lng']}), 4326), '{data['area_code']}', {self.bike_type}, {int(data['parking_spaces'])}) 
            ON CONFLICT (station_id) DO UPDATE SET 
                total_spaces = EXCLUDED.total_spaces;
            """
            )
