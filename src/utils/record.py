import asyncio
import time
from datetime import datetime, timedelta
from typing import List

import aiohttp
import pytz
import requests
from loguru import logger

import utils.database as db


class Record:
    def __init__(self, bike_type: int = 0):
        self.bike_type: int = bike_type
        self.data: List[dict] = []
        self.weather_info = []

    async def start_youbike(self):
        await self.fetch_youbike_data()

        await self.update_youbike()
        logger.info("==========YouBike Record updated==========")

    async def start_weather(self):
        await self.fetch_weather()

        await self.update_weather()
        logger.info("==========Weather Record updated==========")

    async def fetch_youbike_data(self):
        logger.info("Fetching YouBike data with API...")
        start_time = time.time()
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

        end_time = time.time()
        logger.info(
            f"YouBike data fetched. Total stations: {len(self.data)}. Time taken: {end_time - start_time} seconds"
        )

    async def fetch_weather(self):
        start_time = time.time()
        today = datetime.now(pytz.timezone("Asia/Taipei"))
        yesterday = today - timedelta(days=1)
        yesterday_date = yesterday.strftime("%Y-%m-%d")

        # TODO: Extract to a function
        bike_stations = []
        for each in requests.get(
            "https://apis.youbike.com.tw/api/front/station/all?lang=tw&type=1"
        ).json()["retVal"]:
            if each["status"] == 1:
                if each["lat"] != "" and each["lng"] != "":
                    bike_stations.append(each)
        for each in requests.get(
            "https://apis.youbike.com.tw/api/front/station/all?lang=tw&type=2"
        ).json()["retVal"]:
            if each["status"] == 1:
                if each["lat"] != "" and each["lng"] != "":
                    bike_stations.append(each)

        logger.info("Fetching weather info...")
        async with aiohttp.ClientSession() as session:
            tasks = []
            TASK_LIMIT = 75
            stations = [
                bike_stations[i : i + TASK_LIMIT]
                for i in range(0, len(bike_stations), TASK_LIMIT)
            ]

            for index, substations in enumerate(stations):
                logger.debug(f"Running task {index}/{len(stations)}")
                for station in substations:
                    station_no = str(station["station_no"])
                    lat = float(station["lat"])
                    lng = float(station["lng"])
                    tasks.append(
                        asyncio.create_task(
                            self.fetch_weather_info(
                                session, yesterday_date, station_no, lat, lng
                            )
                        )
                    )
                await asyncio.gather(*tasks)

        end_time = time.time()
        logger.info(
            f"Weather info fetched. Total weather info: {len(self.weather_info)}. Time taken: {end_time - start_time} seconds"
        )

    async def fetch_weather_info(
        self,
        session: aiohttp.ClientSession,
        date_str: str,
        station_no: str,
        lat: float,
        lng: float,
    ):
        async with session.get(
            url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,apparent_temperature,precipitation_probability,precipitation,rain,showers,weathercode,pressure_msl,surface_pressure,cloudcover,visibility,evapotranspiration,et0_fao_evapotranspiration,vapor_pressure_deficit,windspeed_10m,windgusts_10m,soil_temperature_0cm,soil_moisture_0_1cm,uv_index,uv_index_clear_sky,cape,freezinglevel_height&timezone=auto&start_date={date_str}&end_date={date_str}"
        ) as weather_response, session.get(
            url=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lng}&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,aerosol_optical_depth,dust,uv_index,uv_index_clear_sky,us_aqi,us_aqi_pm2_5,us_aqi_pm10,us_aqi_no2,us_aqi_co,us_aqi_o3,us_aqi_so2&timezone=auto&start_date={date_str}&end_date={date_str}"
        ) as aq_response:
            weather_json = await weather_response.json()
            aq_json = await aq_response.json()

        for index, weather_time in enumerate(weather_json["hourly"]["time"]):
            self.weather_info.append(
                (
                    int(station_no),
                    datetime.strptime(weather_time, "%Y-%m-%dT%H:%M"),
                    float(weather_json["hourly"]["temperature_2m"][index]),
                    float(weather_json["hourly"]["apparent_temperature"][index]),
                    int(weather_json["hourly"]["relativehumidity_2m"][index]),
                    float(weather_json["hourly"]["dewpoint_2m"][index]),
                    int(weather_json["hourly"]["precipitation_probability"][index]),
                    float(weather_json["hourly"]["precipitation"][index]),
                    float(weather_json["hourly"]["rain"][index]),
                    float(weather_json["hourly"]["showers"][index]),
                    int(weather_json["hourly"]["weathercode"][index]),
                    float(weather_json["hourly"]["pressure_msl"][index]),
                    float(weather_json["hourly"]["surface_pressure"][index]),
                    int(weather_json["hourly"]["cloudcover"][index]),
                    float(weather_json["hourly"]["visibility"][index]),
                    float(weather_json["hourly"]["evapotranspiration"][index]),
                    float(weather_json["hourly"]["et0_fao_evapotranspiration"][index]),
                    float(weather_json["hourly"]["vapor_pressure_deficit"][index]),
                    float(weather_json["hourly"]["windspeed_10m"][index]),
                    float(weather_json["hourly"]["windgusts_10m"][index]),
                    float(weather_json["hourly"]["soil_temperature_0cm"][index]),
                    float(weather_json["hourly"]["soil_moisture_0_1cm"][index]),
                    float(weather_json["hourly"]["uv_index"][index]),
                    float(weather_json["hourly"]["uv_index_clear_sky"][index]),
                    float(weather_json["hourly"]["cape"][index]),
                    float(weather_json["hourly"]["freezinglevel_height"][index]),
                    float(aq_json["hourly"]["pm2_5"][index]),
                    float(aq_json["hourly"]["pm10"][index]),
                    float(aq_json["hourly"]["carbon_monoxide"][index]),
                    float(aq_json["hourly"]["nitrogen_dioxide"][index]),
                    float(aq_json["hourly"]["sulphur_dioxide"][index]),
                    float(aq_json["hourly"]["ozone"][index]),
                    float(aq_json["hourly"]["aerosol_optical_depth"][index]),
                    float(aq_json["hourly"]["dust"][index]),
                    int(aq_json["hourly"]["us_aqi"][index]),
                    int(aq_json["hourly"]["us_aqi_pm2_5"][index]),
                    int(aq_json["hourly"]["us_aqi_pm10"][index]),
                    int(aq_json["hourly"]["us_aqi_no2"][index]),
                    int(aq_json["hourly"]["us_aqi_co"][index]),
                    int(aq_json["hourly"]["us_aqi_o3"][index]),
                    int(aq_json["hourly"]["us_aqi_so2"][index]),
                )
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

        for data in self.weather_info:
            insert_commands.append(data)

        await db.insert_table(table_name="weather", insert_commands=insert_commands)
