from flask import Flask

app = Flask(__name__)


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
                    "periodS": 3600,
                    "value": 0.521
                }
            ]
        },
        "sensors": [
            {
                "type": "activePower",
                "value": 520,
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
