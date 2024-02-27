"""shutterbox simulator

API docs: https://technical.blebox.eu/openapi_shutterbox/openAPI_shutterBox_20190911.html
"""
import random

import itertools
import os
import threading
import time
from enum import IntEnum, StrEnum

from flask import Flask

from ._kit import setup_logging, step_state
from ._common_20190911 import make_blueprint

DEVICE_TYPE = "shutterBox"

VARIANT = os.environ.get("VARIANT", "")
FAULTY = bool(os.environ.get("FAULTY"))

setup_logging(__name__ if not VARIANT else f"{__name__}[{VARIANT}]")
app = Flask(__name__)
app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE, name_suffix=VARIANT))


class StateEnum(IntEnum):
    MOVING_DOWN = 0
    MOVING_UP = 1
    MANUALLY_STOPPED = 2
    LOWER_LIMIT_REACHED = 3
    UPPER_LIMIT_REACHED = 4
    # gatebox states
    OVERLOAD = 5
    MOTOR_FAILURE = 6
    UNUSED = 7
    SAFETY_STOP = 8


class ControlTypeEnum(IntEnum):
    SEGMENTED_SHUTTER = 1
    NO_CALIBRATION = 2
    TILT_SHUTTER = 3
    WINDOW_OPENER = 4
    MATERIAL_SHUTTER = 5
    AWNING = 6
    SCREEN = 7
    CURTAIN = 8


class CommandEnum(StrEnum):
    up = "u"
    down = "d"
    stop = "s"
    next = "n"
    fav = "f"
    up_or_stop = "us"
    down_or_stop = "ds"


INIT_MODE = ControlTypeEnum(int(os.environ.get("MODE", ControlTypeEnum.TILT_SHUTTER)))

STATE_CURRENT = {
    # note: 100 means fully closed, "moving down" means increasing it
    "position": 50,
    "tilt": 0,
}

STATE_DESIRED = {
    "position": 50,
    "tilt": 0,
}

STATE_FAV = {
    "position": 50,
    "tilt": 0,
}

STATE_SHUTTER = {
    "state": StateEnum.UPPER_LIMIT_REACHED,
    "currentPos": STATE_CURRENT,
    "desiredPos": STATE_DESIRED,
    "favPos": STATE_FAV,
}

STATE_SHUTTER_EXTENDED = {
    "calibrationParameters": {
        "isCalibrated": 1,
        "maxMoveTimeUpMs": 32423,
        "maxMoveTimeDownMs": 29815,
        "maxTiltTimeUpMs": 1250,
        "maxTiltTimeDownMs": 1250
    },
    "controlType": INIT_MODE,
}

INTERNAL_STATE = {
    "next": itertools.cycle([
        StateEnum.MOVING_UP,
        StateEnum.MANUALLY_STOPPED,
        StateEnum.MOVING_DOWN,
        StateEnum.MANUALLY_STOPPED
    ])
}

STATE_LOCK = threading.Lock()
INTERNAL_STATE_LOCK = threading.Lock()


def driver(step: float = 5, interval: float = 1):
    while True:
        time.sleep(interval)
        with STATE_LOCK, INTERNAL_STATE_LOCK:
            current_tilt = STATE_CURRENT["tilt"]
            desired_tilt = STATE_DESIRED["tilt"]
            current_pos = STATE_CURRENT["position"]
            desired_pos = STATE_DESIRED["position"]

            if current_tilt == desired_tilt and current_pos == desired_pos:
                continue

            new_tilt = int(step_state(current_tilt, desired_tilt, step))
            new_pos = int(step_state(current_pos, desired_pos, step))
            # todo: set moving state depending on the delta sign
            delta_pos = new_pos - current_pos

            if delta_pos > 0:
                STATE_SHUTTER["state"] = StateEnum.MOVING_DOWN

            if delta_pos < 0:
                STATE_SHUTTER["state"] = StateEnum.MOVING_UP

            if new_pos == desired_pos:
                # note: not sure about this eventual state it may be upper/lower
                #       limit depending on the moving state
                STATE_SHUTTER["state"] = StateEnum.MANUALLY_STOPPED

            if new_pos >= 100:
                new_pos = 100
                STATE_SHUTTER["state"] = StateEnum.LOWER_LIMIT_REACHED

            if new_pos <= 0:
                new_pos = 0
                STATE_SHUTTER["state"] = StateEnum.UPPER_LIMIT_REACHED

            if new_tilt != current_tilt:
                print("state:", StateEnum(STATE_SHUTTER["state"]).name, "tilt ->", new_tilt, flush=True)

            if new_pos != current_pos:
                print("state:", StateEnum(STATE_SHUTTER["state"]).name, "pos ->", new_pos, flush=True)

            STATE_CURRENT["position"] = new_pos
            STATE_CURRENT["tilt"] = new_tilt


# note: this is hacky, it will break autoreload
t = threading.Thread(target=driver, daemon=True)
t.start()


@app.route("/api/shutter/state", methods=["GET"])
def api_shutter_state():
    with STATE_LOCK:
        return {"shutter": {**STATE_SHUTTER}}


@app.route("/api/shutter/extended/state", methods=["GET"])
def api_shutter_extended_state():
    with STATE_LOCK:
        return {"shutter": {**STATE_SHUTTER, ** STATE_SHUTTER_EXTENDED}}


@app.route("/s/<command>", methods=["GET"])
def s_command(command):
    if command not in CommandEnum:
        return f"unrecognized command: <{command}>", 400

    def set_state(state: StateEnum):
        match state:
            case StateEnum.MOVING_UP:
                STATE_DESIRED["position"] = 0
            case StateEnum.MOVING_DOWN:
                STATE_DESIRED["position"] = 100
            case StateEnum.MANUALLY_STOPPED:
                STATE_DESIRED["position"] = STATE_CURRENT["position"]
            case StateEnum.OVERLOAD | StateEnum.MOTOR_FAILURE | StateEnum.SAFETY_STOP:
                STATE_DESIRED["position"] = STATE_CURRENT["position"]
        STATE_SHUTTER["state"] = state

    with STATE_LOCK, INTERNAL_STATE_LOCK:
        current_state = STATE_SHUTTER["state"]

        match command:
            case CommandEnum.up:
                set_state(StateEnum.MOVING_UP)

            case CommandEnum.down:
                if FAULTY:
                    set_state(random.choice([
                        StateEnum.SAFETY_STOP,
                        StateEnum.OVERLOAD,
                        StateEnum.MOTOR_FAILURE
                    ]))
                else:
                    set_state(StateEnum.MOVING_DOWN)

            case CommandEnum.stop:
                set_state(StateEnum.MANUALLY_STOPPED)

            case CommandEnum.down_or_stop:
                if current_state in {StateEnum.MOVING_DOWN, StateEnum.MOVING_UP}:
                    set_state(StateEnum.MANUALLY_STOPPED)
                else:
                    set_state(StateEnum.MOVING_DOWN)

            case CommandEnum.up_or_stop:
                if current_state in {StateEnum.MOVING_DOWN, StateEnum.MOVING_UP}:
                    set_state(StateEnum.MANUALLY_STOPPED)
                else:
                    set_state(StateEnum.MOVING_UP)

        if command == CommandEnum.next:
            while (new := next(INTERNAL_STATE["next"])) != current_state:
                set_state(new)

        return {"shutter": {**STATE_SHUTTER}}


@app.route("/s/t/<int:tilt>")
def s_t_tilt(tilt):
    with STATE_LOCK, INTERNAL_STATE_LOCK:
        STATE_DESIRED["tilt"] = tilt
        return {"shutter": {**STATE_SHUTTER}}


@app.route("/s/p/<int:position>")
def s_p_position(position):
    with STATE_LOCK, INTERNAL_STATE_LOCK:
        STATE_DESIRED["position"] = position
        return {"shutter": {**STATE_SHUTTER}}


@app.route("/s/p/<int:position>/t/<int:tilt>")
def s_p_position_t_tilt(position, tilt):
    with STATE_LOCK, INTERNAL_STATE_LOCK:
        STATE_DESIRED["position"] = position
        STATE_DESIRED["tilt"] = tilt
        return {"shutter": {**STATE_SHUTTER}}
