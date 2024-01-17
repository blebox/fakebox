import math

from werkzeug.exceptions import BadRequest


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
