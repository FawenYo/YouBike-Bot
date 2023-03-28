import re
from datetime import datetime, timedelta

from geopy.distance import geodesic
from googlemaps import Client
from linebot.models import *
from loguru import logger

import config

true = True
gmaps = Client(config.GOOGLE_API_KEY)


class Templates:
    def welcome_message(self):
        message_flex = FlexSendMessage(
            alt_text="歡迎使用 好想騎YouBike",
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://i.imgur.com/3ObOBHW.png",
                    "size": "full",
                    "aspectRatio": "5:4",
                    "aspectMode": "cover",
                    "action": {"type": "uri", "uri": "http://linecorp.com/"},
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "嗨~ 歡迎使用 好想騎YouBike 服務 (-^〇^-)\n由於YouBike公司通知，本服務暫時只能查詢1.0資料，請多包涵\n若有法律疑慮，可通過 ntubike20@gmail.com 聯絡告知",
                            "wrap": true,
                        }
                    ],
                },
            },
        )
        return message_flex

    def bike_data(self, results, user_lat, user_lng, bike_type, action):
        contents = []
        num = 0
        message_contents = []
        for each in results:
            num += 1
            name_tw = each["name_tw"].replace("(", " (")
            available_spaces = str(each["available_spaces"])
            empty_spaces = str(each["empty_spaces"])
            lng = str(each["loc"][0])
            lat = str(each["loc"][1])
            updated_at = str(each["updated_at"]).replace("-", "/")

            if bike_type == 1:
                name_tw = "(1.0) " + name_tw
            else:
                name_tw = "(2.0) " + name_tw

            origin_point = (user_lat, user_lng)
            dist_point = (lat, lng)
            distance = str(round(geodesic(origin_point, dist_point).meters, 2))

            if action == "borrow":
                if int(available_spaces) > 0:
                    bubble = {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/4vK8avw.png",
                            "size": "full",
                            "aspectRatio": "1.7:1",
                            "aspectMode": "cover",
                            "action": {"type": "uri", "uri": "http://linecorp.com/"},
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": name_tw,
                                    "weight": "bold",
                                    "align": "center",
                                    "wrap": true,
                                    "size": "xl",
                                },
                                {"type": "separator", "margin": "sm"},
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "可借車位",
                                                    "wrap": true,
                                                    "align": "center",
                                                    "size": "xl",
                                                },
                                                {
                                                    "type": "text",
                                                    "text": available_spaces,
                                                    "align": "center",
                                                    "wrap": true,
                                                    "size": "3xl",
                                                    "weight": "bold",
                                                    "color": "#00FF00",
                                                },
                                            ],
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "可還車位",
                                                    "align": "center",
                                                    "wrap": true,
                                                    "size": "xl",
                                                },
                                                {
                                                    "type": "text",
                                                    "text": empty_spaces,
                                                    "weight": "bold",
                                                    "size": "3xl",
                                                    "wrap": true,
                                                    "align": "center",
                                                    "color": "#FF0000",
                                                },
                                            ],
                                        },
                                    ],
                                    "margin": "sm",
                                },
                                {
                                    "type": "text",
                                    "text": "和您距離：{}公尺".format(distance),
                                    "wrap": true,
                                    "align": "center",
                                },
                                {"type": "separator", "margin": "md"},
                                {
                                    "type": "text",
                                    "text": "更新時間：{}".format(updated_at),
                                    "margin": "md",
                                    "align": "center",
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "查看路線",
                                        "data": "route_{},{},{},{}".format(
                                            user_lat, user_lng, lat, lng
                                        ),
                                    },
                                    "style": "primary",
                                    "margin": "md",
                                    "color": "#4A89F3",
                                },
                            ],
                        },
                    }
                    contents.append(bubble)
            else:
                if int(empty_spaces) > 0:
                    bubble = {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/4vK8avw.png",
                            "size": "full",
                            "aspectRatio": "1.7:1",
                            "aspectMode": "cover",
                            "action": {"type": "uri", "uri": "http://linecorp.com/"},
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": name_tw,
                                    "weight": "bold",
                                    "align": "center",
                                    "wrap": true,
                                    "size": "xl",
                                },
                                {"type": "separator", "margin": "sm"},
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "可借車位",
                                                    "wrap": true,
                                                    "align": "center",
                                                    "size": "xl",
                                                },
                                                {
                                                    "type": "text",
                                                    "text": available_spaces,
                                                    "align": "center",
                                                    "wrap": true,
                                                    "size": "3xl",
                                                    "weight": "bold",
                                                    "color": "#00FF00",
                                                },
                                            ],
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "可還車位",
                                                    "align": "center",
                                                    "wrap": true,
                                                    "size": "xl",
                                                },
                                                {
                                                    "type": "text",
                                                    "text": empty_spaces,
                                                    "weight": "bold",
                                                    "size": "3xl",
                                                    "wrap": true,
                                                    "align": "center",
                                                    "color": "#FF0000",
                                                },
                                            ],
                                        },
                                    ],
                                    "margin": "sm",
                                },
                                {
                                    "type": "text",
                                    "text": "和您距離：{}公尺".format(distance),
                                    "wrap": true,
                                    "align": "center",
                                },
                                {"type": "separator", "margin": "md"},
                                {
                                    "type": "text",
                                    "text": "更新時間：{}".format(updated_at),
                                    "margin": "md",
                                    "align": "center",
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "查看路線",
                                        "data": "route_{},{},{},{}".format(
                                            user_lat, user_lng, lat, lng
                                        ),
                                    },
                                    "style": "primary",
                                    "margin": "md",
                                    "color": "#4A89F3",
                                },
                            ],
                        },
                    }
                    contents.append(bubble)
        while contents:
            temp = contents[:10]
            flex_message = FlexSendMessage(
                alt_text="腳踏車列表", contents={"type": "carousel", "contents": temp}
            )
            message_contents.append(flex_message)

            contents = contents[10:]
        if len(message_contents) > 5:
            message_contents = message_contents[:5]
        return message_contents

    def route(self, user_lat, user_lng, lat, lng):
        now = datetime.now()
        origin = "{}, {}".format(user_lat, user_lng)
        destination = "{}, {}".format(lat, lng)
        logger.debug(f"directing to {destination} from {origin}")
        response = gmaps.directions(
            origin=origin, destination=destination, mode="walking", language="zh-TW"
        )[0]["legs"][0]
        logger.debug(f"Got response from google maps: {response}")

        start_address = response["start_address"]
        end_address = response["end_address"]
        dureation = response["duration"]["text"]
        directions = response["steps"]

        header_contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "出發地", "color": "#ffffff66", "size": "sm"},
                    {
                        "type": "text",
                        "text": start_address,
                        "color": "#ffffff",
                        "size": "md",
                        "flex": 4,
                        "weight": "bold",
                        "wrap": true,
                    },
                ],
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "目的地", "color": "#ffffff66", "size": "sm"},
                    {
                        "type": "text",
                        "text": end_address,
                        "color": "#ffffff",
                        "size": "md",
                        "flex": 4,
                        "weight": "bold",
                        "wrap": true,
                    },
                ],
            },
        ]
        body_contents = [
            {
                "type": "text",
                "text": "總時間：{}".format(dureation),
                "color": "#b7b7b7",
                "size": "xs",
            }
        ]
        time_consume = 0

        these_regex = "<.*?>"

        for each in directions:
            if time_consume == 0:
                color = "#EF454D"
            else:
                color = "#6486E3"
            time_consume += each["duration"]["value"]
            time_text = "步行" + each["duration"]["text"]
            delta = now + timedelta(seconds=time_consume)
            time = delta.strftime("%H:%M")

            direct_text = re.sub(
                these_regex, "", each["html_instructions"].replace("&nbsp;", "")
            )
            if "目的地" in direct_text:
                des_each = direct_text.split("目的地")
                route_text = "{}{}\n目的地{}".format(
                    des_each[0], each["distance"]["text"], des_each[1]
                )
            else:
                route_text = "{}{}".format(direct_text, each["distance"]["text"])
            loc = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "text", "text": time, "size": "sm", "gravity": "center"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "filler"},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [{"type": "filler"}],
                                "cornerRadius": "30px",
                                "height": "12px",
                                "width": "12px",
                                "borderColor": color,
                                "borderWidth": "2px",
                            },
                            {"type": "filler"},
                        ],
                        "flex": 0,
                    },
                    {
                        "type": "text",
                        "text": route_text,
                        "gravity": "center",
                        "flex": 4,
                        "size": "sm",
                        "wrap": true,
                    },
                ],
                "spacing": "lg",
                "cornerRadius": "30px",
                "margin": "xl",
            }

            body_contents.append(loc)

            if "目的地" not in each["html_instructions"]:
                route_timing = {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [{"type": "filler"}],
                            "flex": 1,
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {"type": "filler"},
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [{"type": "filler"}],
                                            "width": "2px",
                                            "backgroundColor": "#B7B7B7",
                                        },
                                        {"type": "filler"},
                                    ],
                                    "flex": 1,
                                }
                            ],
                            "width": "12px",
                        },
                        {
                            "type": "text",
                            "text": time_text,
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c",
                        },
                    ],
                    "spacing": "lg",
                    "height": "64px",
                }
                body_contents.append(route_timing)

        bubble = {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": header_contents,
                "paddingAll": "20px",
                "backgroundColor": "#0367D3",
                "spacing": "md",
                "height": "154px",
                "paddingTop": "22px",
                "action": {
                    "type": "uri",
                    "label": "查看Google Maps",
                    "uri": "https://www.google.com/maps/search/?api=1&query={},{}&travelmode=walking".format(
                        lat, lng
                    ),
                },
            },
            "body": {"type": "box", "layout": "vertical", "contents": body_contents},
        }
        message_flex = FlexSendMessage(alt_text="路線規劃", contents=bubble)
        return message_flex
