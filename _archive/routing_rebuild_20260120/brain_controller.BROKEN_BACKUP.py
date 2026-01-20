# brain_controller.py
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from hardware_executor import HardwareExecutor
from router_engine import RouterEngine
from kernel_router import RouterState


# -------------------------
# Config
# -------------------------

def _env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return float(v)
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except Exception:
        return default


def _env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None and v != "" else default


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


@dataclass
class Cfg:
    model_dir: str
    audio_device: Optional[int]
    samplerate: int
    wake_threshold: float
    wake_aliases: List[str]
    command_window: float
    tts_mute_base: float
    confirm_accept_delay: float


def load_cfg(args) -> Cfg:
    repo_dir = Path(__file__).resolve().parent
    default_model = str(repo_dir / "vosk-model-small-en-us-0.15")

    model_dir = _env_str("DEMERZEL_VOSK_MODEL", default_model)

    # Device: CLI overrides env; env overrides None (use default input)
    env_dev = os.getenv("DEMERZEL_AUDIO_DEVICE")
    env_dev_i = int(env_dev) if env_dev and env_dev.isdigit() else None
    audio_device = args.device if args.device is not None else env_dev_i

    samplerate = _env_int("DEMERZEL_SAMPLE_RATE", 16000)

    wake_threshold = args.wake_threshold if args.wake_threshold is not None else _env_float("DEMERZEL_WAKE_THRESHOLD", 0.55)

    wake_aliases_raw = _env_str(
        "DEMERZEL_WAKE_ALIASES",
        "demerzel,dan brazil,dan brazel,dan derzel,demersel"
    )
    wake_aliases = [_norm(x) for x in wake_aliases_raw.split(",") if _norm(x)]

    command_window = _env_float("DEMERZEL_COMMAND_WINDOW", 30.0)
    tts_mute_base = _env_float("DEMERZEL_TTS_MUTE", 1.6)
    confirm_accept_delay = _env_float("DEMERZEL_CONFIRM_ACCEPT_DELAY", 1.0)

    return Cfg(
        model_dir=model_dir,
        audio_device=audio_device,
        samplerate=samplerate,
        wake_threshold=wake_threshold,
        wake_aliases=wake_aliases,
        command_window=command_window,
        tts_mute_base=tts_mute_base,
        confirm_accept_delay=confirm_accept_delay,
    )


# -------------------------
# TTS + self-hearing guard
# -------------------------

def say(text: str) -> None:
    # macOS
    if not text:
        return
    subprocess.run(["say", text], check=False)


# -------------------------
# Audio device helpers
# -------------------------

def list_devices() -> None:
    devs = sd.query_devices()
    default_in, default_out = sd.default.device
    print(f"Default device (in,out): [{default_in}, {default_out}]")
    print("\nINPUT devices:")
    for d in devs:
        if d.get("max_input_channels", 0) > 0:
            idx = d["index"]
            mic = d["name"]
            ch = d["max_input_channels"]
            sr = d.get("default_samplerate")
            print(f"  {idx:>2}  in={ch}  sr={sr}  {mic}")


def open_input_stream(device: Optional[int], samplerate: int) -> Tuple[sd.RawInputStream, int]:
    """
    Always open with 1 channel (most built-in mics are mono).
    This avoids PortAudio 'Invalid number of channels' (-9998).
    """
    channels = 1

    # If the device doesn't support requested samplerate, fall back to its default.
    if device is not None:
        info = sd.query_devices(device, "input")
        dev_sr = int(info.get("default_samplerate", samplerate))
    else:
        # default input device info
        info = sd.query_devices(None, "input")
        dev_sr = int(info.get("default_samplerate", samplerate))

    use_sr = samplerate
    try:
        stream = sd.RawInputStream(
            samplerate=use_sr,
            blocksize=8000,
            device=device,
            dtype="int16",
            channels=channels,
        )
        return stream, use_sr
    except Exception:
        # fallback
        use_sr = dev_sr
        stream = sd.RawInputStream(
            samplerate=use_sr,
            blocksize=8000,
            device=device,
            dtype="int16",
            channels=channels,
        )
        return stream, use_sr


# -------------------------
# Wake detection (confidence-based)
# -------------------------

def conf_of_result(result_json: str) -> float:
    try:
        obj = json.loads(result_json)
        words = obj.get("result") or []
        if not words:
            return 0.0
        confs = [w.get("conf", 0.0) for w in words if isinstance(w, dict)]
        if not confs:
            return 0.0
        return sum(confs) / max(1, len(confs))
    except Exception:
        return 0.0


def contains_wake(text: str, aliases: List[str]) -> bool:
    t = _norm(text)
    return any(a and a in t for a in aliases)


# -------------------------
# Main loop
# -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-devices", action="store_true")
    ap.add_argument("--device", type=int, default=None, help="sounddevice input device index")
    ap.add_argument("--wake-threshold", type=float, default=None)
    args = ap.parse_args()

    if args.list_devices:
        list_devices()
        return

    cfg = load_cfg(args)

    print(
        f"[CFG] command_window={cfg.command_window:.1f}s "
        f"tts_mute_base={cfg.tts_mute_base:.2f}s "
        f"confirm_accept_delay={cfg.confirm_accept_delay:.2f}s "
        f"audio_device={cfg.audio_device} "
        f"wake_threshold={cfg.wake_threshold:.2f} "
        f"wake_aliases={len(cfg.wake_aliases)}"
    )

    model_path = Path(cfg.model_dir)
    if not model_path.exists():
        print(f"[ERR] Vosk model not found at: {model_path}")
        print("Put a Vosk model folder there, or set DEMERZEL_VOSK_MODEL=/path/to/model")
        sys.exit(1)

    model = Model(str(model_path))

    hw = HardwareExecutor()
    router_state = RouterState()
    engine = RouterEngine(hw=hw, state=router_state)

    q: "queue.Queue[bytes]" = queue.Queue()
    mute_until = 0.0

    def callback(indata, frames, time_info, status):
        nonlocal q
        if status:
            # keep going; just print once in a while if needed
            pass
        q.put(bytes(indata))

    stream, sr = open_input_stream(cfg.audio_device, cfg.samplerate)
    rec = KaldiRecognizer(model, sr)
    rec.SetWords(True)

    state = "IDLE"
    command_deadline = 0.0

    print("[STATE] IDLE (say 'Demerzel')")

    with stream:
        stream.start()
        while True:
            data = q.get()
            now = time.time()
            if now < mute_until:
                continue

            if rec.AcceptWaveform(data):
                result = rec.Result()
                try:
                    obj = json.loads(result)
                except Exception:
                    obj = {}

                text = (obj.get("text") or "").strip()
                if not text:
                    continue

                # --- IDLE: listen for wake ---
                if state == "IDLE":
                    c = conf_of_result(result)
                    if contains_wake(text, cfg.wake_aliases) and c >= cfg.wake_threshold:
                        say("Yes?")
                        mute_until = time.time() + cfg.tts_mute_base
                        state = "COMMAND"
                        command_deadline = time.time() + cfg.command_window
                        print(f"[WAKE] matched '{text}' (conf={c:.2f})")
                        continue
                    else:
                        # ignore everything else in idle
                        continue

                # --- COMMAND: route one utterance, then keep listening until timeout ---
                if state == "COMMAND":
                    out = engine.route(text)
                    if out.speak:
                        say(out.speak)
                        # stronger mute after prompts, to reduce self-hearing auto-confirm
                        extra = cfg.confirm_accept_delay if ("Say:" in out.speak or "Say " in out.speak) else 0.0
                        mute_until = time.time() + cfg.tts_mute_base + extra

                    # If we timed out, drop back to idle.
                    if time.time() > command_deadline:
                        state = "IDLE"
                        print("[STATE] COMMAND timeout -> IDLE")
                    continue

            else:
                # partials: we *don’t* wake on partials here (more stable)
                if state == "COMMAND" and time.time() > command_deadline:
                    state = "IDLE"
                    print("[STATE] COMMAND timeout -> IDLE")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CTRL-C] clean exit.")

