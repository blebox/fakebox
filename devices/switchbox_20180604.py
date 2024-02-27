"""SwitchboxD simulator

API docs: https://technical.blebox.eu/openapi_switchbox/openAPI_switchBox_20180604.html
"""
from flask import Flask, request
from werkzeug.exceptions import BadRequest

from ._common_20180604 import make_blueprint
from ._kit import require_field, setup_logging

DEVICE_TYPE = "switchBox"

setup_logging(__name__)
app = Flask(__name__)
app.register_blueprint(make_blueprint(api_version=API_VERSION, device_type=DEVICE_TYPE))

STATE_RELAYS = {
    "0": 0,
}


@app.route("/api/relay/state", methods=["GET"])
def api_relay_state():
    # note: in this api level, relay state is just an array. In later versions
    # it is {"relays": []} object
    return [
        {
            "relay": 0,
            "state": STATE_RELAYS["0"]
        },
    ]


@app.route("/api/relay/extended/state", methods=["GET"])
def api_relay_extended_state():
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"],
                "stateAfterRestart": 2,
                "defaultForTime": 0,
            },
        ],
    }


@app.route("/api/relay/set", methods=["POST"])
def api_relay_set():
    relays = require_field(request.json, ".relays")
    if not isinstance(relays, list):
        raise BadRequest("Bad payload: .relays must be a list")

    if not (len(relays) == 1):
        raise BadRequest("Error: this device has only one relay")

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
        ]
    }


@app.route("/s/<state>", methods=["GET"])
def s_state(state):
    relay = "0"
    STATE_RELAYS[relay] = int(not STATE_RELAYS[relay]) if state == 2 else int(state)
    return [
        {
            "relay": 0,
            "state": STATE_RELAYS["0"]
        }
    ]
