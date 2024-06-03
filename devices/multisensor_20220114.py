"""generic multisensor simulator

Important: uses multiSensor API specification
API docs: https://technical.blebox.eu/openapi_multisensor/openAPI_multiSensor_20210413.html
"""
import math
import statistics
import time

from flask import Flask

from ._kit import setup_logging
from ._common_20220114 import make_blueprint

DEVICE_TYPE = "multiSensor"
PRODUCT_NAME = "wind&rain&lightsensor"

setup_logging(__name__)
app = Flask(__name__)
app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE, product=PRODUCT_NAME))


def signal(x):
    return int(abs(math.sin(x)) * 100)


@app.route("/state", methods=["GET"])
def state():
    t = time.time()
    return {
        "multiSensor": {
            "sensors": [
                {
                    "id": 0,
                    "type": "wind",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "windAvg",
                    # avg of last 10 min
                    "value": int(statistics.mean([signal(t-x) for x in range(600)])),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "windMax",
                    # max of last 10 min
                    "value": max(*[signal(t-x) for x in range(600)]),
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "rain",
                    "value": int(math.sin(t) > 0),
                    "state": 2,
                },
                {
                    "type": "illuminance",
                    "id": 2,
                    "value": signal(t),
                    "state": 2
                },
                {
                    "type": "illuminanceAvg",
                    "id": 2,
                    "value": int(statistics.mean([signal(t-x) for x in range(600)])),
                    "state": 2
                },
                {
                    "type": "illuminanceMax",
                    "id": 2,
                    "value": max(*[signal(t-x) for x in range(600)]),
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
                    "type": "wind",
                    "value": signal(t),
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "trend": 1,
                    "name": "wind sensor on roof"
                },
                {
                    "id": 0,
                    "type": "windAvg",
                    # avg of last 10 min
                    "value": int(statistics.mean([signal(t-x) for x in range(600)])),
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "trend": 1,
                    "name": "wind sensor on roof"
                },
                {
                    "id": 0,
                    "type": "windMax",
                    # max of last 10 min
                    "value": max(*[signal(t - x) for x in range(600)]),
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "trend": 1,
                    "name": "wind sensor on roof"
                },
                {
                    "id": 1,
                    "type": "rain",
                    "value": int(math.sin(t) > 0),
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "trend": 1,
                    "name": "rain sensor on porch"
                },
                {
                    "type": "illuminance",
                    "id": 2,
                    "value": signal(t),
                    "trend": 3,
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "name": "illuminance sensor on roof"
                },
                {
                    "type": "illuminanceAvg",
                    "id": 2,
                    "value": int(statistics.mean([signal(t - x) for x in range(600)])),
                    "trend": 3,
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "name": "illuminance sensor on roof"
                },
                {
                    "type": "illuminanceMax",
                    "id": 2,
                    "value": max(*[signal(t - x) for x in range(600)]),
                    "state": 2,
                    "iconSet": 10,
                    "elapsedTimeS": 10,
                    "name": "illuminance sensor on roof"
                }
            ],
            "notConfiguredProbes": 0,
        }
    }
