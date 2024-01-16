"""SwitchboxD simulator

Version:
API docs: https://technical.blebox.eu/openapi_switchboxd/openAPI_switchBoxD_20200831.html
"""
import math
import time

from flask import Flask, request
from werkzeug.exceptions import BadRequest

API_VERSION = "20200831"
START_TIME = time.time()

app = Flask(__name__)

STATE_AP_NETWORK = {
    "apEnable": True,
    "apSSID": "shutterBox-g650e32d2217",
    "apPasswd": "my_secret_password"
}

STATE_NETWORK = {
    "ssid": "WiFi_Name",
    "pwd": "my_secret_password",
    "station_status": 5
}

STATE_RELAYS = {
    "0": 0,
    "1": 0,
}


def synthetic_signal(t: float):
    """Synthetic time-based signal"""
    return math.sin(math.sqrt(t)) + math.cos(t / 2) + 2 + math.cos(math.cos(t))


def t_integral(t0, t1, f, steps=1000):
    """Approximate integral of f() with trapeze method"""
    assert t0 < t1
    area = 0
    delta = t1 - t0
    dx = delta / steps

    for i in range(steps):
        area += ((f(t0 + i * dx)) + f(t0 + (i + 1) * dx)) / 2 * dx
    return area


def require_field(data: dict, path: str, of_type=None, _lead=""):
    assert path.startswith(".")
    assert len(path) > 1

    if not isinstance(data, dict):
        raise BadRequest(f"Bad payload: expected {_lead or 'payload'} to be mapping")

    head, *rest = path[1:].rsplit(".")
    val = data.get(head)

    if head not in data:
        raise BadRequest(f"Bad payload: missing {_lead}.{head} field")

    if rest:
        return require_field(data[head], f".{rest[0]}", of_type=of_type, _lead=f"{_lead}.{head}")

    if of_type and not isinstance(data[head], of_type):
        raise BadRequest(f"Bad payload: {_lead}.{head} has wrong type")

    return val


@app.route("/", methods=["GET"])
def index():
    return "I'm a switchbox"


@app.route("/info", methods=["GET"])
def info():
    return {
        "device": {
            "deviceName": "My SwitchBoxD",
            "type": "switchBoxD",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": "6334f7e750b8",
            "ip": "192.168.1.11"
        }
    }


@app.route("/api/device/uptime", methods=["GET"])
def api_device_uptime():
    return {"upTimeS": time.time() - START_TIME}


@app.route("/api/ota/update", methods=["POST"])
def api_ota_update():
    return


@app.route("/api/device/set", methods=["POST"])
def api_device_set():
    STATE_AP_NETWORK.update({
        "apEnable": require_field(request.json, ".network.apEnable", bool),
        "apSSID": require_field(request.json, ".network.apSSID", str),
        "apPasswd": require_field(request.json, ".network.apPasswd", str),
    })

    return {
        "device": {
            "deviceName": "My BleBox device name",
            "product": "shutterBoxV2",
            "type": "shutterBox",
            "apiLevel": "20200831",
            "hv": "9.1d",
            "fv": "0.987",
            "id": "g650e32d2217",
            "ip": "192.168.1.11"
        },
        "network": {
            "ssid": "WiFi_Name",
            "bssid": "70:4f:25:24:11:ae",
            "ip": "192.168.1.11",
            "mac": "bb:50:ec:2d:22:17",
            "station_status": 5,
            "tunnel_status": 5,
            "channel": 7,
            **STATE_AP_NETWORK,
        }
    }


@app.route("/api/wifi/connect", methods=["POST"])
def api_wifi_connect():
    STATE_NETWORK.update({
        "ssid": require_field(request.json, ".ssid", str),
        "pwd": require_field(request.json, ".pwd", str),
    })
    return {
        "ssid": STATE_NETWORK["ssid"],
        "station_status": STATE_NETWORK["station_status"],
    }


@app.route("/api/wifi/disconnect", methods=["POST"])
def api_wifi_disconnect():
    STATE_NETWORK.update({
        "ssid": require_field(request.json, ".ssid", str),
        "pwd": require_field(request.json, ".pwd", str),
    })
    return {
        "ssid": STATE_NETWORK["ssid"],
        "station_status": STATE_NETWORK["station_status"],
    }


@app.route("/api/device/network", methods=["GET"])
def api_device_network():
    res = {
        **STATE_AP_NETWORK,
        **STATE_NETWORK,
        "bssid": "70:4f:25:24:11:ae",
        "ip": "192.168.1.11",
        "mac": "bb:50:ec:2d:22:17",
        "tunnel_status": 5,
        "apEnable": True,
        "apSSID": "shutterBox-g650e32d2217",
        "apPasswd": "my_secret_password",
        "channel": 7
    }
    res.pop("pwd")
    return res


@app.route("/api/wifi/scan", methods=["GET"])
def api_wifi_scan():
    return {
        "ap": [
            {
                "ssid": "Funny_WiFi_Name",
                "rssi": -60,
                "enc": 3
            },
            {
                "ssid": "Less_Funny_WiFi_Name",
                "rssi": -75,
                "enc": 4
            },
            {
                "ssid": "Not_Funny_WiFi_Name",
                "rssi": -90,
                "enc": 0
            }
        ]
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

    if not (1 <= len(relays) <=2):
        raise BadRequest("Error: this device has only two relays")

    # todo: forTime control
    states = {}
    for i, relay in enumerate(relays):
        lead = f".relays[{i}]"
        idx = require_field(relay, ".relay", int, _lead=lead)
        states[str(idx)] = require_field(relay, ".state", int, _lead=lead)

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
        "powerMeasuring": {
            "enabled": 1,
            "powerConsumption": [
                {
                    "periodS": delta_t,
                    "value": t_integral(t - delta_t, t, synthetic_signal)
                }
            ]
        },
        "sensors": [
            {
                "type": "activePower",
                "value": synthetic_signal(t),
                "trend": 0,
                "state": 4
            }
        ]
    }


@app.route("/s/<relay>/<state>", methods=["GET"])
def s_relay_state(relay, state):
    STATE_RELAYS[relay] = int(state)
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
