from typing import List

from bson.son import SON
from pymongo import GEOSPHERE

import config


def search(
    bike_type: int, latitude: float, longitude: float, max_distance: int
) -> List[dict]:
    """Search nearby YouBike

    Args:
        bike_type (int): YouBike type.
        latitude (float): Latitude of user's location.
        longitude (float): Longitude of user's location.
        max_distance (int): Search radius.

    Returns:
        List[dict]: Search result.
    """
    result = []
    config.db[f"Youbike {bike_type}.0"].create_index([("loc", GEOSPHERE)])
    query = {
        "loc": {
            "$near": SON(
                [
                    (
                        "$geometry",
                        SON(
                            [
                                ("type", "Point"),
                                ("coordinates", [longitude, latitude]),
                            ]
                        ),
                    ),
                    ("$maxDistance", max_distance),
                ]
            )
        }
    }
    for each in config.db[f"Youbike {bike_type}.0"].find(query):
        result.append(each)
    return result
