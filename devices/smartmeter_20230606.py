"""SmartMeter simulator which is a special flavour of multisensor

Important: uses multiSensor API specification
API docs: https://technical.blebox.eu/openapi_multisensor/openAPI_multiSensor_20230606.html
"""
import math
import time

from flask import Flask

from ._kit import setup_logging
from ._common_20230606 import make_blueprint

DEVICE_TYPE = "multiSensor"
PRODUCT_NAME = "SmartMeter"

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
                # first sensor set
                {
                    "id": 0,
                    "type": "forwardActiveEnergy",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "reverseActiveEnergy",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "apparentEnergy",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "activePower",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "apparentPower",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "voltage",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "current",
                    "value": signal(t),
                    "state": 2,
                },
                {
                    "id": 0,
                    "type": "frequency",
                    "value": signal(t),
                    "state": 2,
                },
                # second sensor set
                {
                    "id": 1,
                    "type": "forwardActiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "reverseActiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "apparentEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "activePower",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "apparentPower",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "voltage",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "current",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                {
                    "id": 1,
                    "type": "frequency",
                    "value": signal(t) + 1,
                    "state": 2,
                },
                # third sensor set
                {
                    "id": 2,
                    "type": "forwardActiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "reverseActiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "apparentEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "activePower",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "apparentPower",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "voltage",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "current",
                    "value": signal(t) + 2,
                    "state": 2,
                },
                {
                    "id": 2,
                    "type": "frequency",
                    "value": signal(t) + 2,
                    "state": 2,
                },
            ]
        }
    }


@app.route("/state/extended", methods=["GET"])
def state_extended():
    t = time.time()
    # too many sensors to play with, these do not matter that much for smartmeter
    extra = {
        "iconSet": 10,
        "elapsedTimeS": 10,
        "trend": 1,
        "name": "n/a"
    }

    return {
        "multiSensor": {
            "sensors": [
                # first sensor set
                {
                    "id": 0,
                    "type": "forwardActiveEnergy",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "reverseActiveEnergy",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "apparentEnergy",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "activePower",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "apparentPower",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "voltage",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "current",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                {
                    "id": 0,
                    "type": "frequency",
                    "value": signal(t),
                    "state": 2,
                    **extra,
                },
                # second sensor set
                {
                    "id": 1,
                    "type": "forwardActiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "reverseActiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "apparentEnergy",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "activePower",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "apparentPower",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "voltage",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "current",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 1,
                    "type": "frequency",
                    "value": signal(t) + 1,
                    "state": 2,
                    **extra,
                },
                # third sensor set
                {
                    "id": 2,
                    "type": "forwardActiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "reverseActiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "forwardReactiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "reverseReactiveEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "apparentEnergy",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "activePower",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "apparentPower",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "voltage",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "current",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },
                {
                    "id": 2,
                    "type": "frequency",
                    "value": signal(t) + 2,
                    "state": 2,
                    **extra,
                },

            ],
            "notConfiguredProbes": 0,
        }
    }
