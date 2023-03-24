import time
from typing import Dict, List

import asyncpg
from loguru import logger

import config


async def init_schema() -> None:
    # Connect to PostgreSQL
    conn = await asyncpg.connect(config.pg_conn_info)

    # Execute SQL command from file
    async with conn.transaction():
        with open("utils/scripts/schema.sql", "r") as f:
            await conn.execute(f.read())

    # Close connection
    await conn.close()


async def insert_table(table_name: str, insert_commands: List[tuple]) -> None:
    logger.debug(f"Start to update table {table_name}, inserting {len(insert_commands)} rows...")
    start_time = time.time()

    # Read SQL command from file
    with open(f"utils/scripts/{table_name}_insert.sql", "r") as f:
        _sql_command = f.read()

    # Connect to PostgreSQL
    conn = await asyncpg.connect(config.pg_conn_info)

    # Execute SQL command
    async with conn.transaction():
        await conn.executemany(_sql_command, insert_commands)

    # Close connection
    await conn.close()

    end_time = time.time()
    logger.info(
        f"{table_name}_history table updated. Time taken: {end_time - start_time} seconds"
    )


async def fetch_database_stations(bike_type: int) -> Dict[str, int]:
    """
    Fetch all stations from database
    Args:
        bike_type: Youbike type

    Returns:
        Dict[str, int]: Dictionary of station_id and total_spaces
    """
    logger.debug("Fetching database stations...")
    start_time = time.time()
    stations: Dict[str, int] = {}

    # Read SQL command from file
    with open("utils/scripts/station_select.sql", "r") as f:
        _sql_command = f.read()

    # Connect to PostgreSQL
    conn = await asyncpg.connect(config.pg_conn_info)

    # Execute SQL command
    async with conn.transaction():
        results = await conn.fetch(_sql_command, bike_type)
        for each in results:
            stations[str(each["station_id"])] = int(each["total_spaces"])

    # Close connection
    await conn.close()

    end_time = time.time()
    logger.debug(
        f"Database stations fetched. Total: {len(stations)}. Time taken: {end_time - start_time} seconds"
    )
    return stations
