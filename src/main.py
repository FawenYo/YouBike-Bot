import threading
from datetime import datetime

import pytz
from flask import abort, render_template, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from loguru import logger

import config
from config import app
from search import search
from templates import Templates
from utils.fetch import Data

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
logger.add(config.logging_handler)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    logger.debug("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# PostBack Event
@handler.add(PostbackEvent)
def handle_postback(event):
    # 路線規劃
    if "route" in event.postback.data:
        # Parse data from Postback
        user_lat, user_lng, bike_lat, bike_lng = event.postback.data.split("_")[
            1
        ].split(",")
        message = Templates().route(
            user_lat=user_lat, user_lng=user_lng, lat=bike_lat, lng=bike_lng
        )
        line_bot_api.reply_message(event.reply_token, message)
    # 借 / 還車
    elif "action" in event.postback.data:
        action = event.postback.data.split("_")[1]
        if action == "borrow":
            line_bot_api.link_rich_menu_to_user(
                event.source.user_id, config.RETURN_RICH_MENU
            )
            message = TextSendMessage(text="切換模式：還車")
        else:
            line_bot_api.link_rich_menu_to_user(
                event.source.user_id, config.BORROW_RICH_MENU
            )
            message = TextSendMessage(text="切換模式：借車")
        line_bot_api.reply_message(event.reply_token, message)


# 處理訊息
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    try:
        rich_menu_id = line_bot_api.get_rich_menu_id_of_user(event.source.user_id)
    except:
        rich_menu_id = config.BORROW_RICH_MENU
    if rich_menu_id == config.BORROW_RICH_MENU:
        action = "borrow"
    else:
        action = "return"
    if isinstance(event.message, LocationMessage):
        now = datetime.now(pytz.timezone("Asia/Taipei"))
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        latitude = float(event.message.latitude)
        longitude = float(event.message.longitude)

        youbike_1 = search(
            bike_type=1, latitude=latitude, longitude=longitude, max_distance=500
        )
        youbike_2 = search(
            bike_type=2, latitude=latitude, longitude=longitude, max_distance=200
        )
        if len(youbike_1) == 0 and len(youbike_2) == 0:
            message = TextSendMessage(text="很抱歉！\n您所在的位置附近並沒有YouBike站點！")
            line_bot_api.reply_message(event.reply_token, message)
        else:
            youbike1_data = Templates().bike_data(
                results=youbike_1,
                user_lat=latitude,
                user_lng=longitude,
                bike_type=1,
                action=action,
            )
            youbike2_data = Templates().bike_data(
                results=youbike_2,
                user_lat=latitude,
                user_lng=longitude,
                bike_type=2,
                action=action,
            )
            message = youbike1_data + youbike2_data
            line_bot_api.reply_message(event.reply_token, message)


@handler.add(FollowEvent)
def handle_follow(event):
    now = datetime.now(pytz.timezone("Asia/Taipei"))
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    user = {
        "uuid": event.source.user_id,
        "time": current_time,
        "action": "borrow",
    }
    config.db["User List"].insert(user)
    message = Templates().welcome_message()
    line_bot_api.reply_message(event.reply_token, message)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    config.db["User List"].delete_one({"uuid": event.source.user_id})


@app.route("/")
def index():
    return render_template("Index.html")


@app.route("/update/youbike")
def youbike_update():
    logger.info("==========Start to update Youbike data==========")
    job = threading.Thread(target=Data().update_youbike)
    job.start()
    return "Job started"


@app.route("/update/weather")
def weather_update():
    logger.info("==========Start to update weather data==========")
    job = threading.Thread(target=Data().update_weather)
    job.start()
    return "Job started"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
