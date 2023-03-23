import os

import logging_loki
import pymongo
from dotenv import load_dotenv
from flask import Flask

#########################
# Environment Variables #
#########################

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_CLIENT"))
db = client["Database"]


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BORROW_RICH_MENU = os.getenv("BORROW_RICH_MENU")
RETURN_RICH_MENU = os.getenv("RETURN_RICH_MENU")
OPEN_WEATHER_MAP_API = os.getenv("OPEN_WEATHER_MAP_API")

#########
# Flask #
#########

app = Flask(__name__, static_url_path="/static/")

###########
# Logging #
###########

logging_handler = logging_loki.LokiHandler(
    url=f"{os.getenv('LOKI_HOST')}:{os.getenv('LOKI_PORT')}/loki/api/v1/push",
    tags={"application": "youbike-bot"},
    version="1",
)

##############
# PostgreSQL #
##############

pg_conn_info = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
