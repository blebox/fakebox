"""SwitchboxD simulator

API docs: https://technical.blebox.eu/openapi_switchboxd/openAPI_switchBoxD_20200831.html
"""
import time

from flask import Flask, request
from werkzeug.exceptions import BadRequest

from ._common_20200831 import make_blueprint
from ._kit import synthetic_signal, t_integral, require_field, setup_logging

DEVICE_TYPE = "switchBoxD"

setup_logging(__name__)
app = Flask(__name__)
app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE))

POWER_MEASURING_ENABLED = 1
STATE_RELAYS = {
    "0": 0,
    "1": 0,
}


@app.route("/state", methods=["GET"])
def state():
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            },
            {
                "relay": 1,
                "state": STATE_RELAYS["1"]
            }
        ]
    }


@app.route("/state", methods=["POST"])
def state_post():
    relays = require_field(request.json, ".relays")
    if not isinstance(relays, list):
        raise BadRequest("Bad payload: .relays must be a list")

    if not (1 <= len(relays) <= 2):
        raise BadRequest("Error: this device has only two relays")

    # todo: forTime control
    states = {}
    for i, relay in enumerate(relays):
        lead = f".relays[{i}]"
        idx = str(require_field(relay, ".relay", int, _lead=lead))
        state = require_field(relay, ".state", int, _lead=lead)
        state = int(not STATE_RELAYS[idx]) if state == 2 else int(state)
        states[idx] = state

    if len(states) != len(relays):
        raise BadRequest("Error: duplicated relays")

    STATE_RELAYS.update(states)
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            },
            {
                "relay": 1,
                "state": STATE_RELAYS["1"]
            }
        ]
    }


@app.route("/state/extended", methods=["GET"])
def state_extended():
    # scale to minutes
    t = time.time()
    delta_t = 3600

    if POWER_MEASURING_ENABLED:
        power_measuring = {
            "enabled": 1,
            "powerConsumption": [
                {
                    "periodS": delta_t,

                    # note: let's assume synthetic_signal is power consumption
                    # at the moment in Watts. Itegral will be in Ws. We need to
                    # rescale to keep consistent with activePower
                    "value": t_integral(t - delta_t, t, synthetic_signal) / (1000 * 3600)  # kWh
                }
            ]
        }
    else:
        power_measuring = {"enabled": 0}

    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"],
                "stateAfterRestart": 2,
                "defaultForTime": 0,
                "name": "Output no 1"
            },
            {
                "relay": 1,
                "state": STATE_RELAYS["1"],
                "stateAfterRestart": 2,
                "defaultForTime": 0,
                "name": "Output no 2"
            }
        ],
        "powerMeasuring": power_measuring,
        "sensors": [
            {
                "type": "activePower",
                "value": synthetic_signal(t),  # [Watt]
                "trend": 0,  # not used, always 0
                "state": 4,
            }
        ]
    }


@app.route("/s/<relay>/<state>", methods=["GET"])
def s_relay_state(relay, state):
    STATE_RELAYS[relay] = int(not STATE_RELAYS[relay]) if state == 2 else int(state)
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            },
            {
                "relay": 1,
                "state": STATE_RELAYS["1"]
            }
        ]
    }
