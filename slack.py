import json

import requests


def post_to_slack(text: str, post_url: str):
    payload = {
        "username": "wordle solver",
        "icon_emoji": ":alphabet-white-w:",
        "text": text,
    }

    payloadJson = json.dumps(payload)
    res = requests.post(post_url, data=payloadJson)
    return res
