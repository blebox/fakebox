"""SwitchboxD simulator

API docs: https://technical.blebox.eu/openapi_wlightbox/openAPI_wLightBox_20200229.html

Important: wLightBox and wLightBoxS have really complex API. This module is highly
incomplete.
"""
import json
import os
from enum import IntEnum

from itertools import zip_longest

from flask import Flask, request

from ._common_20200229 import make_blueprint
from ._kit import require_field, setup_logging

DEVICE_TYPE = "wLightBox"

setup_logging(__name__)
app = Flask(__name__)


class BleboxColorMode(IntEnum):
    RGBW = 1  # RGB color-space with color brightness, white brightness
    RGB = 2  # RGB color-space with color brightness
    MONO = 3
    RGBorW = 4  # RGBW entity, where white color is prioritised
    CT = 5  # color-temperature, brightness, effect
    CTx2 = 6  # color-temperature, brightness, effect, two instances
    RGBWW = 7  # RGB with two color-temperature sliders(warm, cold)


INIT_MODE = BleboxColorMode(int(os.environ.get("MODE", BleboxColorMode.CTx2)))

app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE, name_suffix=INIT_MODE.name))

STATE_RGBW = {
    # modes according to docs
    # * 1 RGBW
    # * 2 RGB
    # * 3 MONO: 4 separated channel (LED strips)
    # * 4 RGBorW: RGBW but with exceptive parts: color (RGB) and white (W), where
    #     white (W) part has priority*
    # * 5 CT (color temperature). For one 2-channel LED strips
    #     (warm white - 1:(R); cold white - 1:(G))
    # * 6 CTx2: 2 separated LED strips (color temperature)
    #     For two separated 2-channel LED strips
    #     (warm white - 1:(R),2:(B); cold white - 1:(G),2:(W)
    # Note: support for mode 7 (RGBWW) missing
    "colorMode": INIT_MODE,
    "effectID": 2,
    "desiredColor": "ff003000",
    "currentColor": "ff003000",
    "lastOnColor": "ff003000",
    "durationsMs": {},
}

STATE_RGBW_EXTENDED = {
    "effectNames": {
        "0": "NONE",
        "1": "FADE",
        "2": "RGB",
        "3": "POLICE",
        "4": "RELAX",
        "5": "STROBO",
        "6": "BELL"
    },
    "favColors": {
        "0": "ff000000",
        "1": "00ff0000",
        "2": "0000ff00",
        "3": "000000ff",
        "4": "00000000",
        "5": "ff00ff00",
        "6": "ffff0000",
        "7": "00ffff00",
        "8": "ff800000",
        "9": "0080ff00"
    },
}


def apply_color(original: str, new: str, color_mode=None):
    # note: logic here is strange, not sure if W priority works that way
    #       needs to be checked with real device
    if color_mode == 4 and original[-2:] != new[-2:]:
        new = "------" + new[-2:]

    if color_mode == 2:
        new = new[:4] + "00"

    v = []
    for o, n in zip_longest(original, new, fillvalue="-"):
        v.append(n if n != "-" else o)
    return "".join(v)


@app.route("/api/rgbw/state", methods=["GET"])
def api_rgbw_state():
    return {
        "rgbw": STATE_RGBW
    }


@app.route("/api/rgbw/set", methods=["POST"])
def api_rgbw_set():
    # note: wlightbox always expects JSON and does not look at content type.
    #       Also, homeassistant doesn't send content-type header. Probably should.
    payload = json.loads(request.data)
    rgbw = require_field(payload, ".rgbw", of_type=dict)

    effect_id = STATE_RGBW["effectID"]
    desired_color = STATE_RGBW["desiredColor"]

    if "effectID" in rgbw:
        effect_id = require_field(rgbw, ".effectID", of_type=int)

    if "desiredColor" in rgbw:
        requested = require_field(rgbw, ".desiredColor", of_type=str)
        print("color prev:", desired_color)
        print("color req: ", requested)
        desired_color = apply_color(desired_color, requested, STATE_RGBW["colorMode"])
        print("color next:", desired_color)

    STATE_RGBW.update({
        "effectID": effect_id,
        "desiredColor": desired_color,
        # note: skipping durationMs for now
    })

    return {
        "rgbw": STATE_RGBW
    }


@app.route("/api/rgbw/extended/state", methods=["GET"])
def api_rgbw_extended_state():
    return {
        "rgbw": {
            **STATE_RGBW,
            **STATE_RGBW_EXTENDED,
        }
    }
