import math
import time

from flask import Flask

app = Flask(__name__)


def synthetic_signal(t: float):
    """Synthetic time-based signal"""
    return math.sin(math.sqrt(t)) + math.cos(t/2) + 2 + math.cos(math.cos(t))


def t_integral(t0, t1, f, steps=1000):
    """Approximate integral of f() with trapeze method"""
    assert t0 < t1
    area = 0
    delta = t1 - t0
    dx = delta/steps

    for i in range(steps):
        area += ((f(t0 + i*dx)) + f(t0 + (i + 1) * dx)) / 2 * dx
    return area


@app.route("/", methods=["GET"])
def index():
    return "I'm a switchbox"


@app.route("/info", methods=["GET"])
def info():
    return {
        "device": {
            "deviceName": "My SwitchBoxD",
            "type": "switchBoxD",
            "apiLevel": "20220114",
            "hv": "0.2",
            "fv": "0.247",
            "id": "6334f7e750b8",
            "ip": "192.168.1.11"
        }
    }


@app.route("/api/device/uptime", methods=["GET"])
def uptime():
    return {
        "upTimeS": 243269
    }


@app.route("/api/device/network", methods=["GET"])
def network():
    return {
        "ssid": "WiFi_Name",
        "bssid": "70:4f:25:24:11:ae",
        "ip": "192.168.1.11",
        "mac": "bb:50:ec:2d:22:17",
        "station_status": 5,
        "tunnel_status": 5,
        "apEnable": True,
        "apSSID": "shutterBox-g650e32d2217",
        "apPasswd": "my_secret_password",
        "channel": 7
    }


@app.route("/api/wifi/scan", methods=["GET"])
def wifi_scan():
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
                "state": relays["0"]
            },
            {
                "relay": 1,
                "state": relays["1"]
            }
        ]
    }


relays = {
    "0": 0,
    "1": 0,
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
                "state": relays["0"],
                "stateAfterRestart": 2,
                "defaultForTime": 0,
                "name": "Output no 1"
            },
            {
                "relay": 1,
                "state": relays["1"],
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
                    "value": t_integral(t-delta_t, t, synthetic_signal)
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
def set_relay_state(relay, state):
    relays[relay] = int(state)
    return {
        "relays": [
            {
                "relay": 0,
                "state": relays["0"]
            },
            {
                "relay": 1,
                "state": relays["1"]
            }
        ]
    }
