#!/usr/bin/env python3
"""
brain_controller.py

Voice shell with constraints-first execution:
- Wake -> COMMAND mode
- Allowlisted hardware intents:
    PING / LED ON / LED OFF (risk class from ALLOWLIST.json)
    HIGH => 2-step: confirm -> i'm sure

Robust confirmation upgrade:
- Confirm-1 accepts: confirm / yes / ok / okay / do it
- Confirm-2 accepts any phrase containing an "i'm sure" variant:
    "i m sure", "im sure", "i am sure", "i'm sure"
  even if repeated or wrapped (e.g., "yes i'm sure", "i'm sure i'm sure").
- Echo suppression will NEVER discard valid confirmation tokens.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pyaudio
from rapidfuzz import fuzz
from vosk import Model, KaldiRecognizer


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def now_s() -> float:
    return time.time()


def clean_text(s: str) -> str:
    s = (s or "").strip().lower()
    # Normalize punctuation into spaces so "i'm" -> "i m"
    s = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in s)
    return " ".join(s.split())


def say_mac(text: str, voice: str = "Samantha") -> None:
    text = (text or "").strip()
    if not text:
        return
    try:
        subprocess.run(["say", "-v", voice, text], check=False)
    except Exception:
        pass


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except Exception:
        return float(default)


@dataclass
class Config:
    model_path: str
    device_index: int
    wake_threshold: float

    sample_rate: int = 16000
    frame_ms: int = 40

    command_window: float = _env_float("DEMERZEL_COMMAND_WINDOW", 30.0)
    confirm_window: float = _env_float("DEMERZEL_CONFIRM_WINDOW", 20.0)

    # Keep modest: rely on prompt-text filtering, not long mic mutes.
    tts_mic_gate_seconds: float = _env_float("DEMERZEL_TTS_MUTE", 1.0)

    post_wake_cooldown_seconds: float = 0.70

    # Echo comparison window for near-immediate TTS pickup
    anti_echo_window: float = 1.2

    min_final_chars_command: int = 3

    tts_voice: str = os.environ.get("DEMERZEL_VOICE", "Samantha")


def _load_allowlist_commands() -> dict:
    p = repo_root() / "ALLOWLIST.json"
    if not p.exists():
        p = repo_root() / "allowlist.json"
    if not p.exists():
        return {"HIGH": [], "MEDIUM": [], "SAFE": []}
    try:
        data = json.loads(p.read_text())
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"HIGH": [], "MEDIUM": [], "SAFE": []}


def _risk_for_command(cmd_u: str, allow: dict) -> Optional[str]:
    cmd_u = (cmd_u or "").strip().upper()
    for risk in ("HIGH", "MEDIUM", "SAFE"):
        arr = allow.get(risk, [])
        if isinstance(arr, list) and cmd_u in [str(x).strip().upper() for x in arr]:
            return risk
    return None


SPEECH_CANON_ALIASES = {
    "paying": "ping",
    "payin": "ping",
    "pain": "ping",
    "pings": "ping",
    "pinging": "ping",
    "lights on": "led on",
    "light on": "led on",
    "lights off": "led off",
    "light off": "led off",
}


def canonicalize_for_allowlisted_actions(text: str) -> str:
    t = clean_text(text)
    return SPEECH_CANON_ALIASES.get(t, t)


CONFIRM1_TOKENS = {
    "confirm",
    "yes",
    "ok",
    "okay",
    "do it",
}


IM_SURE_PATTERNS = (
    "i m sure",
    "i am sure",
    "im sure",
    "i'm sure",  # will usually normalize to "i m sure", but keep for safety
)


def is_confirm1_phrase(t: str) -> bool:
    t = clean_text(t)
    return t in CONFIRM1_TOKENS


def contains_im_sure_phrase(t: str) -> bool:
    """
    Accept confirm-2 if the transcript CONTAINS an "i'm sure" variant,
    even with repeats or filler words.

    Example accepted:
      "yes i m sure"
      "i m sure i m sure"
      "okay i am sure"
    """
    t = clean_text(t)
    # direct contains
    if any(p in t for p in IM_SURE_PATTERNS):
        return True

    # Allow "sure" only if it's strongly anchored to "i"/"im"/"i am"
    # (prevents accidental "sure" from being enough)
    if "sure" in t:
        if "i " in (t + " ") or t.startswith("i "):
            return True
        if t.startswith("im ") or " im " in f" {t} ":
            return True
        if "i am" in t:
            return True

    return False


class BrainController:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.model = Model(cfg.model_path)
        self.rec = KaldiRecognizer(self.model, cfg.sample_rate)

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.q: "queue.Queue[bytes]" = queue.Queue()

        self.state = "IDLE"
        self.state_deadline = 0.0

        self.command_gate_until = 0.0

        self.last_tts_text = ""
        self.last_tts_time = 0.0
        self.mic_gate_until = 0.0

        self.wake_aliases = [
            "demerzel",
            "demersel",
            "demersle",
            "dam merzel",
            "dammers",
            "dammerzle",
            "dam brazil",
            "dan brazil",
            "dan derzel",
            "dan nizzle",
        ]

        self.allow = _load_allowlist_commands()

        self.pending_cmd: Optional[str] = None
        self.pending_risk: Optional[str] = None
        self.pending_step: int = 0
        self.pending_deadline: float = 0.0

        self.hw = None
        try:
            from hardware_executor import HardwareExecutor  # type: ignore
            self.hw = HardwareExecutor()
        except Exception:
            self.hw = None

    def _callback(self, in_data, frame_count, time_info, status):
        self.q.put(in_data)
        return (None, pyaudio.paContinue)

    def _open_stream(self) -> None:
        if self.stream is not None:
            return
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.cfg.sample_rate,
            input=True,
            input_device_index=self.cfg.device_index,
            frames_per_buffer=int(self.cfg.sample_rate * (self.cfg.frame_ms / 1000.0)),
            stream_callback=self._callback,
        )
        self.stream.start_stream()

    def say(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        print(f"[SAY] {text}")

        self.last_tts_text = clean_text(text)
        self.last_tts_time = now_s()
        self.mic_gate_until = now_s() + float(self.cfg.tts_mic_gate_seconds)

        say_mac(text, voice=self.cfg.tts_voice)

    def _wake_match(self, final_text: str) -> Tuple[bool, float, str]:
        t = clean_text(final_text)
        best = ("", 0.0)
        for a in self.wake_aliases:
            score = fuzz.partial_ratio(t, clean_text(a)) / 100.0
            if score > best[1]:
                best = (a, score)
        return (best[1] >= self.cfg.wake_threshold, best[1], best[0])

    def _start_pending(self, cmd_u: str, risk: str, step: int) -> None:
        self.pending_cmd = cmd_u
        self.pending_risk = risk
        self.pending_step = step
        self.pending_deadline = now_s() + float(self.cfg.confirm_window)
        self.state_deadline = max(self.state_deadline, self.pending_deadline)

    def _clear_pending(self) -> None:
        self.pending_cmd = None
        self.pending_risk = None
        self.pending_step = 0
        self.pending_deadline = 0.0

    def _pending_expired(self) -> bool:
        return bool(self.pending_cmd) and now_s() > self.pending_deadline

    def _execute_hw_command(self, cmd_u: str) -> bool:
        if self.hw is None:
            self.say("Hardware executor not available.")
            return True

        cmd_u = cmd_u.strip().upper()
        try:
            if cmd_u == "PING":
                r = self.hw.ping()
            elif cmd_u == "LED ON":
                r = self.hw.led_on()
            elif cmd_u == "LED OFF":
                r = self.hw.led_off()
            else:
                self.say("Refusing: unknown hardware command.")
                return True

            out = getattr(r, "out", None)
            if isinstance(r, str):
                self.say(r)
            elif out is not None:
                self.say(str(out).strip() or str(r))
            else:
                self.say(str(r))
            return True
        except Exception as e:
            self.say(f"ERROR: hardware failed: {e}")
            return True

    def _prompt_like_echo(self, heard: str) -> bool:
        """
        Treat these as prompt-ish (likely self audio) and ignore them.
        Confirmation tokens are NEVER filtered as echo.
        """
        h = clean_text(heard)

        # Never ignore actual confirmation tokens:
        if self.pending_cmd and self.pending_step == 1 and is_confirm1_phrase(h):
            return False
        if self.pending_cmd and self.pending_step == 2 and contains_im_sure_phrase(h):
            return False

        # Strong prompt markers:
        markers = (
            "action requested",
            "say confirm",
            "are you sure",
            "high risk",
            "say i m sure",
            "say i am sure",
            "say im sure",
        )
        if any(m in h for m in markers):
            return True

        # Very-near-time echo of our last TTS (tight window)
        if self.last_tts_text and (now_s() - self.last_tts_time) < float(self.cfg.anti_echo_window):
            if fuzz.partial_ratio(h, self.last_tts_text) >= 90:
                return True

        return False

    def _handle_allowlisted_hardware(self, final_text: str) -> bool:
        if self.hw is None:
            return False

        if self._pending_expired():
            print("[GATE] confirm window expired -> clearing pending + returning to IDLE")
            self._clear_pending()
            self.state = "IDLE"
            return True

        t_raw = clean_text(final_text)
        if not t_raw:
            return False

        t = canonicalize_for_allowlisted_actions(t_raw)
        if t != t_raw:
            print(f"[NORM] '{t_raw}' -> '{t}'")

        if self._prompt_like_echo(t):
            print(f"[ECHO] ignored: {t!r}")
            return True

        # Pending confirmations first
        if self.pending_cmd:
            if self.pending_step == 1:
                print(f"[CONFIRM-1 HEARD] {t!r}")
                if is_confirm1_phrase(t):
                    if self.pending_risk == "HIGH":
                        self.pending_step = 2
                        self.pending_deadline = now_s() + float(self.cfg.confirm_window)
                        self.state_deadline = max(self.state_deadline, self.pending_deadline)
                        self.say("Are you sure? This is HIGH risk. Say: I'm sure.")
                        return True
                    else:
                        cmd = self.pending_cmd
                        self._clear_pending()
                        return self._execute_hw_command(cmd)
                return True

            if self.pending_step == 2:
                print(f"[CONFIRM-2 HEARD] {t!r}")
                if contains_im_sure_phrase(t):
                    cmd = self.pending_cmd
                    self._clear_pending()
                    return self._execute_hw_command(cmd)
                return True

        # No pending: match allowlisted actions
        if t == "ping":
            cmd_u = "PING"
        elif t == "led on":
            cmd_u = "LED ON"
        elif t == "led off":
            cmd_u = "LED OFF"
        else:
            return False

        risk = _risk_for_command(cmd_u, self.allow)
        if risk is None:
            self.say(f"Refusing: {cmd_u} is not allowlisted.")
            return True

        if risk == "HIGH":
            self._start_pending(cmd_u, "HIGH", step=1)
            self.say(f"HIGH action requested: {cmd_u}. Say: confirm.")
            return True

        if risk == "MEDIUM":
            self._start_pending(cmd_u, "MEDIUM", step=1)
            self.say(f"MEDIUM action requested: {cmd_u}. Say: confirm.")
            return True

        return self._execute_hw_command(cmd_u)

    def run(self) -> None:
        self._open_stream()
        print("[STATE] IDLE")
        print(
            f"[CFG] command_window={self.cfg.command_window}s "
            f"confirm_window={self.cfg.confirm_window}s "
            f"tts_mute={self.cfg.tts_mic_gate_seconds}s"
        )

        try:
            while True:
                chunk = self.q.get()
                if now_s() < self.mic_gate_until:
                    continue

                if self.rec.AcceptWaveform(chunk):
                    try:
                        j = json.loads(self.rec.Result() or "{}")
                    except Exception:
                        j = {}

                    final_text = (j.get("text") or "").strip()
                    ft = clean_text(final_text)
                    if not ft:
                        continue

                    if now_s() < self.command_gate_until:
                        continue

                    # COMMAND timeout only when not waiting for confirmation
                    if self.state == "COMMAND" and not self.pending_cmd:
                        if now_s() > self.state_deadline:
                            print("[STATE] COMMAND timeout -> IDLE")
                            self.state = "IDLE"
                            continue

                    if self.state == "IDLE":
                        matched, score, best_alias = self._wake_match(ft)
                        if not matched:
                            continue
                        print(f"[WAKE] matched '{best_alias}' (score={score:.2f})")
                        self.say("Yes?")

                        self.state = "COMMAND"
                        self.state_deadline = now_s() + float(self.cfg.command_window)
                        self.command_gate_until = now_s() + float(self.cfg.post_wake_cooldown_seconds)
                        continue

                    if self.state == "COMMAND":
                        if len(ft) < self.cfg.min_final_chars_command and ft not in ("ok", "yes", "confirm", "sure"):
                            continue

                        if self._handle_allowlisted_hardware(ft):
                            continue

                        # Safe default: ignore unknown commands for now.

        except KeyboardInterrupt:
            print("\n[CTRL-C] clean exit.")
        finally:
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
            except Exception:
                pass
            try:
                self.audio.terminate()
            except Exception:
                pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--device", type=int, default=int(os.environ.get("DEMERZEL_DEVICE", "0")))
    parser.add_argument("--model", type=str, default=os.environ.get("DEMERZEL_MODEL", "vosk-model-small-en-us-0.15"))
    parser.add_argument("--wake-threshold", type=float, default=_env_float("DEMERZEL_CONFIRM_THRESH", 0.62))
    args = parser.parse_args()

    cfg = Config(model_path=args.model, device_index=args.device, wake_threshold=args.wake_threshold)

    if args.list_devices:
        pa = pyaudio.PyAudio()
        info = pa.get_host_api_info_by_index(0)
        n = info.get("deviceCount", 0)
        for i in range(n):
            d = pa.get_device_info_by_host_api_device_index(0, i)
            if int(d.get("maxInputChannels", 0)) > 0:
                print(f"[{i}] {d.get('name')}")
        pa.terminate()
        return

    BrainController(cfg).run()


if __name__ == "__main__":
    main()

