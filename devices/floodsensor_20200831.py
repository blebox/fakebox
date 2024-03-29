"""floodsensor simulator

Important: uses multiSensor API specification
API docs: https://technical.blebox.eu/openapi_multisensor/openAPI_multiSensor_20200831.html
"""
import math
import time

from flask import Flask

from ._kit import setup_logging
from ._common_20200831 import make_blueprint

DEVICE_TYPE = "multiSensor"
PRODUCT_NAME = "floodsensor"

setup_logging(__name__)
app = Flask(__name__)
app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE, product=PRODUCT_NAME))


@app.route("/state", methods=["GET"])
def state():
    t = time.time()

    return {
      "multiSensor": {
        "sensors": [
          {
            "id": 0,
            "type": "flood",
            "value": int(math.sin(t) > 0),
            "state": 2
          },
          {
            "id": 0,
            "type": "floodLastStart",
            "value": 1695033824,
            "state": 2
          },
          {
            "id": 0,
            "type": "floodDuration",
            "value": 168353,
            "state": 2
          }
        ]
      }
    }


@app.route("/state/extended", methods=["GET"])
def state_extended():
    t = time.time()

    return {
        "multiSensor": {
            "sensors": [
                {
                    "id": 0,
                    "type": "flood",
                    "value": int(math.sin(t) > 0),
                    "state": 2,
                    "iconSet": 10
                },
                {
                    "id": 0,
                    "type": "floodLastStart",
                    "value": 1695033824,
                    "state": 2,
                    "iconSet": 10
                },
                {
                    "id": 0,
                    "type": "floodDuration",
                    "value": 168353,
                    "state": 2,
                    "iconSet": 10
                }
            ]
        }
    }
