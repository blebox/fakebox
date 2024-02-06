import time

from flask import Blueprint, request

from . import _kit as kit


def make_blueprint(*, api_version: str, device_type: str, product: str = None):
    bp = Blueprint('myblueprint', __name__)
    ref_time = time.time()

    device_name = f"My {product or device_type} (v{api_version})"
    device_id = kit.device_id(product or device_type, api_version)
    ap_ssid = f"{product or device_type}-g650e32d2217"

    state_ap_network = {
        "apEnable": True,
        "apSSID": ap_ssid,
        "apPasswd": "my_secret_password"
    }

    state_network = {
        "ssid": "WiFi_Name",
        "pwd": "my_secret_password",
        "station_status": 5
    }

    @bp.route("/", methods=["GET"])
    def index():
        return f"I'm a {device_name}"

    @bp.route("/info", methods=["GET"])
    def info():
        return {
            "device": {
                "deviceName": device_name,
                "type": device_type,
                "product": product,
                "apiLevel": api_version,
                "hv": "0.2",
                "fv": "0.247",
                "id": device_id,
                "ip": "192.168.1.12"
            }
        }

    @bp.route("/api/device/state", methods=["GET"])
    def api_device_state():
        return {
            "device": {
                "deviceName": device_name,
                "type": device_type,
                "product": product,
                "apiLevel": api_version,
                "hv": "0.2",
                "fv": "0.247",
                "id": device_id,
                "ip": "192.168.1.13"
            }
        }

    @bp.route("/api/device/uptime", methods=["GET"])
    def api_device_uptime():
        return {"upTimeS": time.time() - ref_time}

    @bp.route("/api/ota/update", methods=["POST"])
    def api_ota_update():
        return

    @bp.route("/api/device/network", methods=["GET"])
    def api_device_network():
        res = {
            **state_ap_network,
            **state_network,
            "bssid": "70:4f:25:24:11:ae",
            "ip": "192.168.1.11",
            "mac": "bb:50:ec:2d:22:17",
            "tunnel_status": 5,
            "apEnable": True,
            "apSSID": ap_ssid,
            "apPasswd": "my_secret_password",
            "channel": 7
        }
        res.pop("pwd")
        return res

    @bp.route("/api/device/set", methods=["POST"])
    def api_device_set():
        state_ap_network.update({
            "apEnable": kit.require_field(request.json, ".network.apEnable", bool),
            "apSSID": kit.require_field(request.json, ".network.apSSID", str),
            "apPasswd": kit.require_field(request.json, ".network.apPasswd", str),
        })

        return {
            "device": {
                "deviceName": device_name,
                "product": product,
                "type": device_type,
                "apiLevel": api_version,
                "hv": "0.2",
                "fv": "0.247",
                "id": device_id,
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
                **state_ap_network,
            }
        }

    @bp.route("/api/wifi/scan", methods=["GET"])
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

    @bp.route("/api/wifi/connect", methods=["POST"])
    def api_wifi_connect():
        state_ap_network.update({
            "ssid": kit.require_field(request.json, ".ssid", str),
            "pwd": kit.require_field(request.json, ".pwd", str),
        })
        return {
            "ssid": state_network["ssid"],
            "station_status": state_network["station_status"],
        }

    @bp.route("/api/wifi/disconnect", methods=["POST"])
    def api_wifi_disconnect():
        state_network.update({
            "ssid": kit.require_field(request.json, ".ssid", str),
            "pwd": kit.require_field(request.json, ".pwd", str),
        })
        return {
            "ssid": state_network["ssid"],
            "station_status": state_network["station_status"],
        }

    return bp
