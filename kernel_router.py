# kernel_router.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import os
import re
import subprocess
import sys

# We expect your project to have hardware_executor.py in the same folder.
# This router will adapt to whatever API it exposes.
import hardware_executor


# ----------------------------
# Public types (used by brain_controller)
# ----------------------------

@dataclass
class RouterEffects:
    enter_sleep_mode: bool = False


@dataclass
class RouterState:
    # Keep minimal state; expand later if you want memory, confirmations, etc.
    last_text: str = ""
    last_intent: str = ""


@dataclass
class RouterOutput:
    new_state: RouterState
    effects: RouterEffects
    speak: str

    # Useful debug fields (safe for printing/logs)
    did_action: bool = False
    action_name: str = ""
    debug: Dict[str, Any] = field(default_factory=dict)


# ----------------------------
# Intent parsing
# ----------------------------

_RE_PING = re.compile(r"\bping\b", re.I)
_RE_SLEEP = re.compile(r"\b(sleep|go to sleep|stand by|standby)\b", re.I)

# lights/led on/off
_RE_ON = re.compile(r"\b(lights?\s+on|led\s+on|turn\s+on\s+the\s+lights?)\b", re.I)
_RE_OFF = re.compile(r"\b(lights?\s+off|led\s+off|turn\s+off\s+the\s+lights?)\b", re.I)


def route_text(text: str, state: Optional[RouterState] = None) -> RouterOutput:
    if state is None:
        state = RouterState()

    raw = (text or "").strip()
    t = raw.lower().strip()

    new_state = RouterState(last_text=raw, last_intent=state.last_intent)
    effects = RouterEffects()

    # SLEEP
    if _RE_SLEEP.search(raw):
        effects.enter_sleep_mode = True
        new_state.last_intent = "SLEEP"
        return RouterOutput(
            new_state=new_state,
            effects=effects,
            speak="Okay. Going to sleep.",
            did_action=True,
            action_name="SLEEP",
            debug={"matched": "sleep"},
        )

    # PING
    if _RE_PING.search(raw):
        ok, out, err, rc, dbg = _hardware_action("PING")
        new_state.last_intent = "PING"
        return RouterOutput(
            new_state=new_state,
            effects=effects,
            speak=out if ok else f"Hardware error: {err}".strip(),
            did_action=ok,
            action_name="PING",
            debug=dbg,
        )

    # LIGHTS / LED ON
    if _RE_ON.search(raw):
        ok, out, err, rc, dbg = _hardware_action("LED ON")
        new_state.last_intent = "LED ON"
        return RouterOutput(
            new_state=new_state,
            effects=effects,
            speak=out if ok else f"Hardware error: {err}".strip(),
            did_action=ok,
            action_name="LED ON",
            debug=dbg,
        )

    # LIGHTS / LED OFF
    if _RE_OFF.search(raw):
        ok, out, err, rc, dbg = _hardware_action("LED OFF")
        new_state.last_intent = "LED OFF"
        return RouterOutput(
            new_state=new_state,
            effects=effects,
            speak=out if ok else f"Hardware error: {err}".strip(),
            did_action=ok,
            action_name="LED OFF",
            debug=dbg,
        )

    # Unknown
    return RouterOutput(
        new_state=RouterState(last_text=raw, last_intent="UNKNOWN"),
        effects=effects,
        speak="I didn't catch a command.",
        did_action=False,
        action_name="",
        debug={"matched": "none"},
    )


# ----------------------------
# Hardware adapter (robust)
# ----------------------------

def _hardware_action(action: str) -> Tuple[bool, str, str, int, Dict[str, Any]]:
    """
    Returns: ok, out, err, rc, debug
    Normalizes output to a short speakable string (like 'ACK PING').
    """
    dbg: Dict[str, Any] = {"action": action}

    # 1) Try module-level call patterns
    module_fn_names = [
        "send_to_arduino",
        "run_action",
        "execute_action",
        "execute",
        "run",
        "call",
        "dispatch",
    ]
    for fn_name in module_fn_names:
        fn = getattr(hardware_executor, fn_name, None)
        if callable(fn):
            try:
                res = fn(action)
                ok, out, err, rc = _normalize_hw_result(res)
                dbg["path"] = f"module.{fn_name}"
                return ok, out, err, rc, dbg
            except TypeError:
                # Some APIs may want tokens instead of a string
                try:
                    tokens = action.split()
                    res = fn(tokens)
                    ok, out, err, rc = _normalize_hw_result(res)
                    dbg["path"] = f"module.{fn_name}(tokens)"
                    return ok, out, err, rc, dbg
                except Exception as e:
                    dbg["module_call_error"] = f"{fn_name}: {e}"
            except Exception as e:
                dbg["module_call_error"] = f"{fn_name}: {e}"

    # 2) Try HardwareExecutor class patterns
    cls = getattr(hardware_executor, "HardwareExecutor", None)
    if cls is not None:
        try:
            hw = cls()
            dbg["has_hw_class"] = True

            # Common explicit methods
            if action.upper() == "PING":
                for m in ["ping", "do_ping", "ping_arduino"]:
                    meth = getattr(hw, m, None)
                    if callable(meth):
                        res = meth()
                        ok, out, err, rc = _normalize_hw_result(res)
                        dbg["path"] = f"HardwareExecutor.{m}()"
                        return ok, out, err, rc, dbg

            if action.upper() in ["LED ON", "LED_ON"]:
                for m in ["led_on", "set_led_on", "on"]:
                    meth = getattr(hw, m, None)
                    if callable(meth):
                        res = meth()
                        ok, out, err, rc = _normalize_hw_result(res)
                        dbg["path"] = f"HardwareExecutor.{m}()"
                        return ok, out, err, rc, dbg
                # Some APIs expose led(True)
                for m in ["led", "set_led", "set_led_state"]:
                    meth = getattr(hw, m, None)
                    if callable(meth):
                        try:
                            res = meth(True)
                            ok, out, err, rc = _normalize_hw_result(res)
                            dbg["path"] = f"HardwareExecutor.{m}(True)"
                            return ok, out, err, rc, dbg
                        except TypeError:
                            pass

            if action.upper() in ["LED OFF", "LED_OFF"]:
                for m in ["led_off", "set_led_off", "off"]:
                    meth = getattr(hw, m, None)
                    if callable(meth):
                        res = meth()
                        ok, out, err, rc = _normalize_hw_result(res)
                        dbg["path"] = f"HardwareExecutor.{m}()"
                        return ok, out, err, rc, dbg
                for m in ["led", "set_led", "set_led_state"]:
                    meth = getattr(hw, m, None)
                    if callable(meth):
                        try:
                            res = meth(False)
                            ok, out, err, rc = _normalize_hw_result(res)
                            dbg["path"] = f"HardwareExecutor.{m}(False)"
                            return ok, out, err, rc, dbg
                        except TypeError:
                            pass

            # Generic “string command” methods on the instance
            for m in ["send_to_arduino", "execute", "run", "call", "dispatch", "command"]:
                meth = getattr(hw, m, None)
                if callable(meth):
                    try:
                        res = meth(action)
                        ok, out, err, rc = _normalize_hw_result(res)
                        dbg["path"] = f"HardwareExecutor.{m}('{action}')"
                        return ok, out, err, rc, dbg
                    except Exception as e:
                        dbg["hw_call_error"] = f"{m}: {e}"

        except Exception as e:
            dbg["hw_init_error"] = str(e)

    # 3) Last resort: direct SSH call to Pi (only used if your hardware_executor API is totally unknown)
    ok, out, err, rc = _ssh_fallback(action)
    dbg["path"] = "ssh_fallback"
    return ok, out, err, rc, dbg


def _normalize_hw_result(res: Any) -> Tuple[bool, str, str, int]:
    """
    Supports:
    - plain string: "ACK PING"
    - tuple: (ok, out, err, rc)
    - object with attributes: ok/out/err/rc  (like HWResult)
    """
    if res is None:
        return False, "", "No response from hardware layer", 1

    if isinstance(res, str):
        s = res.strip()
        return (True, s, "", 0) if s else (False, "", "Empty response", 1)

    if isinstance(res, tuple) and len(res) == 4:
        ok, out, err, rc = res
        return bool(ok), str(out).strip(), str(err).strip(), int(rc)

    # HWResult-like
    ok = getattr(res, "ok", None)
    out = getattr(res, "out", None)
    err = getattr(res, "err", None)
    rc = getattr(res, "rc", None)
    if ok is not None or out is not None or err is not None or rc is not None:
        out_s = (out or "").strip()
        err_s = (err or "").strip()
        rc_i = int(rc) if rc is not None else (0 if ok else 1)
        ok_b = bool(ok) if ok is not None else (rc_i == 0 and out_s != "")
        # Prefer short "ACK ..." speak text
        speak = out_s if out_s else ("OK" if ok_b else "")
        return ok_b, speak, err_s, rc_i

    # Unknown type: stringify
    s = str(res).strip()
    return (True, s, "", 0) if s else (False, "", "Unknown hardware result type", 1)


def _ssh_fallback(action: str) -> Tuple[bool, str, str, int]:
    """
    Uses SSH directly to run arduino_cmd.py on the Pi.
    Env overrides:
      DEMERZEL_PI_USER, DEMERZEL_PI_HOST, DEMERZEL_ARDUINO_CMD_PATH
    Defaults match what you've been using.
    """
    user = os.environ.get("DEMERZEL_PI_USER", "moketchup")
    host = os.environ.get("DEMERZEL_PI_HOST", "192.168.0.161")
    script = os.environ.get("DEMERZEL_ARDUINO_CMD_PATH", "/home/moketchup/arduino_cmd.py")

    token = action.strip().upper().replace(" ", "_")  # PING / LED_ON / LED_OFF

    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        f"{user}@{host}",
        f"python3 {script} {token}",
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        ok = (p.returncode == 0) and (out != "")
        # Speak the stdout if present; else short error
        speak = out if out else ""
        return ok, speak, err if err else ("SSH fallback failed" if not ok else ""), p.returncode
    except Exception as e:
        return False, "", str(e), 1

