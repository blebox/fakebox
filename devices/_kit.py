import hashlib
import logging
import math
import sys

from werkzeug.exceptions import BadRequest


# todo: make two param
def device_id(name_ref: str, ver_ref: str):
    """Return consistently unique device ID for (device name, api version) pair

    Example usage:

        @app.route("/api/device/state", methods=["GET"])
        def info():
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
    """
    return hashlib.md5(f"{name_ref}-{ver_ref}".encode()).hexdigest()


def synthetic_signal(t: float):
    """Synthetic time-based signal"""
    # squeeze the X axis to have a nicely looking time history
    x = t / 10000
    return math.sin(math.sqrt(x)) + math.cos(x / 2) + 2 + math.cos(math.cos(x))


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


def setup_logging(name: str):
    prefix = name.rsplit(".", 1)[-1]
    formatter = logging.Formatter(f"{prefix: <19} > %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger("werkzeug")
    logger.handlers.append(handler)
