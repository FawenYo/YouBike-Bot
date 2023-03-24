import asyncio
import os
from datetime import datetime
from typing import Dict, List

import aiohttp
from loguru import logger

import utils.database as db


class Record:
    def __init__(self, bike_type: int):
        self.bike_type: int = bike_type
        self.data: List[dict] = []
        self.weather_info = {}

    async def start(self):
        await asyncio.gather(
            self.fetch_youbike_data(),
            self.fetch_weather(),
        )

        await self.update_youbike()
        await self.update_weather()

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
        insert_commands: List[tuple[int, datetime, int]] = []
        insert_stations: List[tuple[int, float, float, str, int, int]] = []
        await db.init_schema()
        db_stations = await db.fetch_database_stations(bike_type=self.bike_type)

        logger.info("Parsing YouBike data...")

        for each in self.data:
            station_no = int(each["station_no"])

            data = (
                station_no,
                datetime.strptime(each["updated_at"], "%Y-%m-%d %H:%M:%S"),
                int(each["available_spaces"]),
            )

            station_data = (
                station_no,
                float(each["lat"]),
                float(each["lng"]),
                str(each["area_code"]),
                self.bike_type,
                int(each["parking_spaces"]),
            )

            # Check if the station is not in the database
            if str(station_no) not in db_stations:
                insert_stations.append(station_data)
            else:
                # Check if the station has changed
                if int(each["parking_spaces"]) != db_stations[str(station_no)]:
                    insert_stations.append(station_data)

            insert_commands.append(data)

        await db.insert_table(table_name="station", insert_commands=insert_stations)
        await db.insert_table(table_name="bike", insert_commands=insert_commands)

    async def update_weather(self):
        insert_commands = []
        logger.info("Parsing weather data...")

        for station_no in self.weather_info:
            data = self.weather_info[station_no]

            insert_commands.append(data)

        await db.insert_table(table_name="weather", insert_commands=insert_commands)
