"""gateBox simulator

API docs: https://technical.blebox.eu/openapi_gatebox/openAPI_gateBox_20230102.html
"""
import itertools
import os
import threading
import time
from enum import IntEnum, StrEnum

from flask import Flask

from ._kit import setup_logging, step_state
from ._common_20230102 import make_blueprint

DEVICE_TYPE = "gateBox"

VARIANT = os.environ.get("VARIANT", "")

setup_logging(__name__ if not VARIANT else f"{__name__}[{VARIANT}]")
app = Flask(__name__)
app.register_blueprint(make_blueprint(device_type=DEVICE_TYPE, name_suffix=VARIANT))


class OutputStateEnum(IntEnum):
    NOT_TRIGGERED = 0
    TRIGGERED = 1


class GateTypeEnum(IntEnum):
    SLIDING_DOOR = 0
    GARAGE_DOOR = 1
    OVER_DOOR = 2
    DOOR = 3


class OutputEnum(IntEnum):
    PRIMARY = 1
    SECONDARY = 2


class PositionStateEnum(IntEnum):
    UNKNOWN = -1
    FULLY_CLOSED = 0
    HALF_OPEN = 50
    FULLY_OPEN = 100


class OpenCloseModeEnum(IntEnum):
    STEP_BY_STEP = 0
    ONLY_OPEN = 1
    OPEN_CLOSE = 2


class ExtraButtonTypeEnum(IntEnum):
    DISABLED = 0
    STOP = 1
    WALK_IN = 2
    OTHER = 3


class InputsTypeEnum(IntEnum):
    METHOD_1 = 0
    METHOD_2 = 1
    METHOD_3 = 2
    DISABLED = 3


class MovementEnum(IntEnum):
    DOWN = 0
    UP = 1
    STOP = 2


class CommandEnum(StrEnum):
    primary = "p"
    secondary = "s"
    open = "o"
    close = "c"
    next = "n"


STATE_CURRENT = {
    # note: 100 means fully closed, "moving down" means increasing it
    "position": 50,
}

STATE_DESIRED = {
    "position": 50,
}

STATE_GATE = {
    "gateOutputState": OutputStateEnum.NOT_TRIGGERED,
    "extraButtonOutputState": OutputStateEnum.NOT_TRIGGERED,
}

INIT_MODE = OpenCloseModeEnum(int(os.environ.get("MODE", OpenCloseModeEnum.STEP_BY_STEP)))

STATE_GATE_EXTENDED = {
    "openCloseMode": INIT_MODE,
    "gateType": GateTypeEnum.GARAGE_DOOR,
    "gatePulseTimeMs": 20000,
}

INTERNAL_STATE = {
    "real_position": 50,
    "last_pulse": OutputEnum.PRIMARY,
    "primary_activated": 0,
    "secondary_activated": 0,
    "next": itertools.cycle([
        MovementEnum.UP,
        MovementEnum.STOP,
        MovementEnum.DOWN,
        MovementEnum.STOP
    ])
}

STATE_LOCK = threading.Lock()
INTERNAL_STATE_LOCK = threading.Lock()


def driver(step: float = 5, interval: float = 1):
    while True:
        time.sleep(interval)

        real_position = INTERNAL_STATE["real_position"]
        desired_position = STATE_DESIRED["position"]
        is_moving = real_position != desired_position

        def desire(position: PositionStateEnum):
            nonlocal desired_position
            STATE_DESIRED["position"] = position
            desired_position = position

        def decide_movement() -> MovementEnum:
            direction = next(INTERNAL_STATE["next"])

            # note: it may happen that gate stopped by itself. If that's the case next
            # gets out of sync, and we need to move extra step
            if is_moving and direction in (MovementEnum.UP, MovementEnum.DOWN):
                direction = next(INTERNAL_STATE["next"])
            elif not is_moving and direction == MovementEnum.STOP:
                direction = next(INTERNAL_STATE["next"])

            return direction

        with STATE_LOCK, INTERNAL_STATE_LOCK:
            if STATE_GATE_EXTENDED["openCloseMode"] == OpenCloseModeEnum.OPEN_CLOSE:
                if INTERNAL_STATE["primary_activated"]:
                    desire(PositionStateEnum.FULLY_OPEN)
                if INTERNAL_STATE["secondary_activated"]:
                    desire(PositionStateEnum.FULLY_CLOSED)

            else:
                if INTERNAL_STATE["primary_activated"]:
                    movement = decide_movement()

                    match movement:
                        case MovementEnum.UP:
                            desire(PositionStateEnum.FULLY_OPEN)
                        case MovementEnum.DOWN:
                            desire(PositionStateEnum.FULLY_CLOSED)
                        case MovementEnum.STOP:
                            desire(real_position)

                if INTERNAL_STATE["secondary_activated"]:
                    # in this mode secondary acts as a stop button
                    desire(real_position)

            new_position = int(step_state(real_position, desired_position, step))

            if new_position != real_position:
                print("gate moved ->", new_position, flush=True)

            INTERNAL_STATE["real_position"] = int(step_state(real_position, desired_position, step))

            # note: we are canceling pulses at every tick
            INTERNAL_STATE["primary_activated"] = 0
            INTERNAL_STATE["secondary_activated"] = 0
            STATE_GATE["gateOutputState"] = OutputStateEnum.NOT_TRIGGERED
            STATE_GATE["extraButtonOutputState"] = OutputStateEnum.NOT_TRIGGERED


# note: this is hacky, it will break autoreload
t = threading.Thread(target=driver, daemon=True)
t.start()


def position_as_enum(position: int) -> PositionStateEnum:
    if position <= 0:
        return PositionStateEnum.FULLY_CLOSED
    if position >= 100:
        return PositionStateEnum.FULLY_OPEN
    return PositionStateEnum.HALF_OPEN


@app.route("/state", methods=["GET"])
def state():
    with STATE_LOCK:
        return {"gate": {
            "currentPos": position_as_enum(INTERNAL_STATE["real_position"]),
            **STATE_GATE,
        }}


@app.route("/state/extended", methods=["GET"])
def state_extended():
    with STATE_LOCK:
        return {"gate": {
            "currentPos": position_as_enum(INTERNAL_STATE["real_position"]),
            **STATE_GATE,
            **STATE_GATE_EXTENDED,
        }}


def driver_pulse_primary():
    INTERNAL_STATE["last_pulse"] = OutputEnum.PRIMARY
    INTERNAL_STATE["primary_activated"] = time.time()
    INTERNAL_STATE["secondary_activated"] = 0
    STATE_GATE["gateOutputState"] = OutputStateEnum.TRIGGERED
    STATE_GATE["extraButtonOutputState"] = OutputStateEnum.NOT_TRIGGERED


def driver_pulse_secondary():
    INTERNAL_STATE["last_pulse"] = OutputEnum.SECONDARY
    INTERNAL_STATE["primary_activated"] = 0
    INTERNAL_STATE["secondary_activated"] = time.time()
    STATE_GATE["gateOutputState"] = OutputStateEnum.NOT_TRIGGERED
    STATE_GATE["extraButtonOutputState"] = OutputStateEnum.TRIGGERED


def driver_pulse_reverse():
    match INTERNAL_STATE["last_pulse"]:
        case OutputEnum.PRIMARY:
            driver_pulse_secondary()

        case OutputEnum.SECONDARY:
            driver_pulse_primary()


def execute_command(command):
    if command not in CommandEnum:
        return f"unrecognized command: <{command}>", 400

    with STATE_LOCK, INTERNAL_STATE_LOCK:
        mode = STATE_GATE_EXTENDED["openCloseMode"]
        position = position_as_enum(INTERNAL_STATE["real_position"])

        match mode:
            case OpenCloseModeEnum.STEP_BY_STEP:
                match command:
                    case CommandEnum.open:
                        if position == PositionStateEnum.FULLY_CLOSED:
                            driver_pulse_primary()
                        if position == PositionStateEnum.FULLY_OPEN:
                            pass
                        else:
                            return "can't execute", 409
                    case CommandEnum.close:
                        if position == PositionStateEnum.FULLY_OPEN:
                            driver_pulse_primary()
                        if position == PositionStateEnum.FULLY_CLOSED:
                            pass
                        else:
                            return "can't execute", 409
                    case CommandEnum.next:
                        driver_pulse_primary()
                    # note: these work the same regardless of the mode
                    case CommandEnum.primary:
                        driver_pulse_primary()
                    case CommandEnum.secondary:
                        driver_pulse_secondary()

            case OpenCloseModeEnum.ONLY_OPEN:
                match command:
                    case CommandEnum.open:
                        driver_pulse_primary()
                    case CommandEnum.close:
                        return "can't execute", 409
                    case CommandEnum.next:
                        driver_pulse_primary()
                    # ditto
                    case CommandEnum.primary:
                        driver_pulse_primary()
                    case CommandEnum.secondary:
                        driver_pulse_secondary()

            case OpenCloseModeEnum.OPEN_CLOSE:
                match command:
                    case CommandEnum.open:
                        driver_pulse_primary()
                    case CommandEnum.close:
                        driver_pulse_secondary()
                    case CommandEnum.next:
                        driver_pulse_reverse()
                    # ditto
                    case CommandEnum.primary:
                        driver_pulse_primary()
                    case CommandEnum.secondary:
                        driver_pulse_secondary()

        return {"shutter": {**STATE_GATE}}


@app.route("/s/<command>", methods=["GET"])
def s_command(command):
    return execute_command(command)


@app.route("/s/<command>", methods=["POST"])
def post_s_command(command):
    return execute_command(command)
