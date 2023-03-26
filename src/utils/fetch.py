import asyncio

import requests
from loguru import logger

import config
import utils.record


class Data:
    def update_youbike(self) -> None:
        """Update database"""
        asyncio.run(self.fetch_youbike(bike_type=1))
        asyncio.run(self.fetch_youbike(bike_type=2))

    def update_weather(self) -> None:
        """Update database"""
        asyncio.run(self.fetch_weather())

    async def fetch_youbike(self, bike_type: int) -> None:
        """Fetch YouBike data with API

        Args:
            bike_type (int): YouBike bike type.
        """
        logger.debug(f"Fetching Youbike {bike_type} data")
        data = requests.get(
            f"https://apis.youbike.com.tw/api/front/station/all?lang=tw&type={bike_type}"
        ).json()

        # Latest data
        for each in data["retVal"]:
            try:
                each["loc"] = [float(each["lng"]), float(each["lat"])]
            except ValueError:
                each["loc"] = [0.0, 0, 0]

            # Delete unnecessary info
            del each["lng"]
            del each["lat"]
            del each["country_code"]
            del each["area_code"]
            del each["type"]
            del each["status"]
            del each["name_en"]
            del each["district_en"]
            del each["address_en"]
            del each["name_cn"]
            del each["district_cn"]
            del each["address_cn"]
            del each["available_spaces_detail"]
            del each["img"]

        logger.debug(f"Updating MongoDB with Youbike {bike_type} data")
        config.db[f"Youbike {bike_type}.0"].drop()
        config.db[f"Youbike {bike_type}.0"].insert_many(data["retVal"])

        logger.debug(f"Initalizing PostgreSQL with Youbike {bike_type} data")
        record = utils.record.Record(bike_type=bike_type)
        await record.start_youbike()

    async def fetch_weather(self) -> None:
        """Fetch weather data with API"""
        record = utils.record.Record()
        await record.start_weather()
