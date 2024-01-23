"""SwitchboxD simulator

Version:
API docs: https://technical.blebox.eu/openapi_switchboxd/openAPI_switchBoxD_20200831.html
"""
import time

from flask import Flask, request
from werkzeug.exceptions import BadRequest

from .kit import synthetic_signal, t_integral, require_field, device_id

API_VERSION = "20200831"
START_TIME = time.time()

app = Flask(__name__)

STATE_AP_NETWORK = {
    "apEnable": True,
    "apSSID": "switchBoxD-g650e32d2217",
    "apPasswd": "my_secret_password"
}

STATE_NETWORK = {
    "ssid": "WiFi_Name",
    "pwd": "my_secret_password",
    "station_status": 5
}

POWER_MEASURING_ENABLED = 1

STATE_RELAYS = {
    "0": 0,
    "1": 0,
}


@app.route("/", methods=["GET"])
def index():
    return f"I'm a SwitchboxD (v{API_VERSION})"


@app.route("/info", methods=["GET"])
def info():
    return {
        "device": {
            "type": "switchBoxD",
            "product": "switchBoxD",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": device_id(__name__),
            "ip": "192.168.1.11"
        }
    }


# deprecated
@app.route("/api/device/state", methods=["GET"])
def api_device_state():
    return {
        "device": {
            "deviceName": f"My SwitchBoxD (v{API_VERSION})",
            "type": "switchBoxD",
            "product": "switchBoxD",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": device_id(__name__),
            "ip": "192.168.1.11"
        }
    }


@app.route("/api/device/uptime", methods=["GET"])
def api_device_uptime():
    return {"upTimeS": time.time() - START_TIME}


@app.route("/api/ota/update", methods=["POST"])
def api_ota_update():
    return


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
        "apSSID": "switchBoxD-g650e32d2217",
        "apPasswd": "my_secret_password",
        "channel": 7
    }
    res.pop("pwd")
    return res


@app.route("/api/device/set", methods=["POST"])
def api_device_set():
    STATE_AP_NETWORK.update({
        "apEnable": require_field(request.json, ".network.apEnable", bool),
        "apSSID": require_field(request.json, ".network.apSSID", str),
        "apPasswd": require_field(request.json, ".network.apPasswd", str),
    })

    return {
        "device": {
            "type": "switchBoxD",
            "product": "switchBoxD",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": device_id(__name__),
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
