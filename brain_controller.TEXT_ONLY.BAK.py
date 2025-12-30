# brain_controller.py
from __future__ import annotations

import os
import re
import sys
import time
import subprocess
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple


# -------------------------
# Binding Constitution
# -------------------------

class State(Enum):
    IDLE = auto()
    WAKE_ACK = auto()
    COMMAND_WINDOW = auto()
    CONFIRMATION_PENDING = auto()
    EXECUTION = auto()
    RESPONSE = auto()
    RETURN_TO_IDLE = auto()


INTENTS = {"PING", "TIME_QUERY", "LED_ON", "LED_OFF", "SLEEP", "UNKNOWN"}

YES_SET = {"yes", "y", "yeah", "yep", "affirmative", "ok", "okay", "sure"}
NO_SET = {"no", "n", "nope", "negative", "cancel"}


@dataclass(frozen=True)
class KernelResult:
    intent: str
    confidence: float
    require_confirmation: bool
    clarification_question: Optional[str] = None
    speak_text: Optional[str] = None  # what to say in RESPONSE
    # action params could go here later (binding: executor only uses explicit mappings)


@dataclass
class Config:
    # Timing (binding defaults)
    command_window_sec: float = float(os.environ.get("DEMERZEL_COMMAND_WINDOW", "3.0"))
    confirm_window_sec: float = float(os.environ.get("DEMERZEL_CONFIRM_WINDOW", "3.5"))

    # Confirmation policy
    confirm_confidence_threshold: float = float(os.environ.get("DEMERZEL_CONFIRM_THRESH", "0.90"))

    # Speech
    enable_tts: bool = os.environ.get("DEMERZEL_TTS", "0") == "1"  # default OFF (text-only safety)
    tts_voice: str = os.environ.get("DEMERZEL_TTS_VOICE", "")  # optional macOS voice name

    # Debug
    debug: bool = os.environ.get("DEMERZEL_DEBUG", "0") == "1"

    # Wake aliases (binding: fuzzy tolerated; here we do textual aliasing in text runner)
    wake_aliases: Tuple[str, ...] = (
        "demerzel",
        "dam er zel",
        "dam erzel",
        "dam brazil",
        "dan er zel",
        "dan erzel",
        "damerzel",
        "demersel",
        "demersel",
    )


class BrainController:
    """
    Binding implementation:
      - Exactly 7 states
      - Silence by default
      - Single speech surface (WAKE_ACK + RESPONSE only)
      - Router proposes only; executor executes only in EXECUTION
    """

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or Config()
        self.state: State = State.IDLE

        self._command_deadline: float = 0.0
        self._confirm_deadline: float = 0.0

        self._pending: Optional[KernelResult] = None
        self._last_response_text: Optional[str] = None

    # -------------------------
    # Logging (never spoken)
    # -------------------------
    def log(self, msg: str) -> None:
        if self.cfg.debug:
            print(msg, flush=True)

    # -------------------------
    # Speech surface (only allowed in WAKE_ACK and RESPONSE)
    # -------------------------
    def say(self, text: str) -> None:
        # Binding: debug must never be spoken -> we only speak provided text.
        self._last_response_text = text

        # Always print for observability in text mode:
        print(f"SAY: {text}", flush=True)

        # Optional macOS TTS (explicitly enabled)
        if self.cfg.enable_tts:
            try:
                cmd = ["say"]
                if self.cfg.tts_voice.strip():
                    cmd += ["-v", self.cfg.tts_voice.strip()]
                cmd += [text]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                # Failure behavior: prefer silence, never crash
                pass

    # -------------------------
    # State transitions
    # -------------------------
    def _enter_idle(self) -> None:
        self.state = State.IDLE
        self._pending = None
        self._command_deadline = 0.0
        self._confirm_deadline = 0.0

    def _enter_wake_ack(self) -> None:
        self.state = State.WAKE_ACK

    def _enter_command_window(self) -> None:
        self.state = State.COMMAND_WINDOW
        self._command_deadline = time.time() + self.cfg.command_window_sec

    def _enter_confirmation(self, kr: KernelResult) -> None:
        self.state = State.CONFIRMATION_PENDING
        self._pending = kr
        self._confirm_deadline = time.time() + self.cfg.confirm_window_sec

    def _enter_execution(self, kr: KernelResult) -> None:
        self.state = State.EXECUTION
        self._pending = kr

    def _enter_response(self) -> None:
        self.state = State.RESPONSE

    def _enter_return_to_idle(self) -> None:
        self.state = State.RETURN_TO_IDLE

    # -------------------------
    # Public events for runners
    # -------------------------
    def on_wake(self) -> None:
        # Binding: wake detector only allowed in IDLE
        if self.state != State.IDLE:
            return

        self.log("[WAKE] accepted")
        self._enter_wake_ack()

        # Binding: ack exactly once per wake
        self.say("Yes.")

        # Immediately open command window (bounded)
        self._enter_command_window()

    def on_final_text(self, text: str) -> None:
        """Called only when STT is permitted. Runner enforces that; controller also gates by state."""
        text = (text or "").strip()
        if not text:
            return

        now = time.time()

        # COMMAND_WINDOW: accept one final, route it, then proceed
        if self.state == State.COMMAND_WINDOW:
            if now > self._command_deadline:
                self.log("[STATE] command timeout -> IDLE")
                self._enter_idle()
                return

            kr = self.route(text)
            self.log(f"[ROUTER] {kr.intent} conf={kr.confidence:.2f} confirm={kr.require_confirmation}")

            if kr.clarification_question:
                # Clarification is a RESPONSE, then IDLE (bounded attention)
                self._enter_response()
                self.say(kr.clarification_question)
                self._enter_return_to_idle()
                self._enter_idle()
                return

            if kr.intent == "UNKNOWN":
                # Optional minimal response, then silence
                if kr.speak_text:
                    self._enter_response()
                    self.say(kr.speak_text)
                self._enter_return_to_idle()
                self._enter_idle()
                return

            if kr.require_confirmation:
                # Ask confirm (RESPONSE), then CONFIRMATION_PENDING
                self._enter_response()
                self.say("Confirm? yes or no.")
                self._enter_confirmation(kr)
                return

            # No confirmation required -> execute
            self._enter_execution(kr)
            result_text = self.execute(kr)
            self._enter_response()
            self.say(result_text)
            self._enter_return_to_idle()
            self._enter_idle()
            return

        # CONFIRMATION_PENDING: only accept yes/no (or route other text as clarification)
        if self.state == State.CONFIRMATION_PENDING:
            if now > self._confirm_deadline:
                self.log("[STATE] confirm timeout -> IDLE")
                self._enter_idle()
                return

            t = self.clean(text)

            if t in YES_SET:
                kr = self._pending
                if not kr:
                    self._enter_idle()
                    return
                self._enter_execution(kr)
                result_text = self.execute(kr)
                self._enter_response()
                self.say(result_text)
                self._enter_return_to_idle()
                self._enter_idle()
                return

            if t in NO_SET:
                self._enter_response()
                self.say("Canceled.")
                self._enter_return_to_idle()
                self._enter_idle()
                return

            # If user says something else, bind: treat as new command attempt but still bounded
            kr2 = self.route(text)
            if kr2.clarification_question:
                self._enter_response()
                self.say(kr2.clarification_question)
                self._enter_return_to_idle()
                self._enter_idle()
                return

            # If it’s a real intent, we re-ask confirm rather than executing silently
            self._enter_response()
            self.say("Confirm? yes or no.")
            # keep confirmation pending (deadline unchanged)
            return

        # Other states: ignore (binding)
        return

    def tick(self) -> None:
        """Call periodically to enforce bounded windows."""
        now = time.time()
        if self.state == State.COMMAND_WINDOW and now > self._command_deadline:
            self.log("[STATE] command timeout -> IDLE")
            self._enter_idle()
        elif self.state == State.CONFIRMATION_PENDING and now > self._confirm_deadline:
            self.log("[STATE] confirm timeout -> IDLE")
            self._enter_idle()

    # -------------------------
    # Router (propose only)
    # -------------------------
    def clean(self, s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def route(self, text: str) -> KernelResult:
        t = self.clean(text)

        # Wake words should NOT be treated as intents inside command window (binding)
        if any(self.clean(a) == t for a in self.cfg.wake_aliases):
            return KernelResult(
                intent="UNKNOWN",
                confidence=0.99,
                require_confirmation=False,
                speak_text=None,  # silence is success
            )

        # PING
        if t in {"ping", "test", "are you there"}:
            return KernelResult(intent="PING", confidence=0.95, require_confirmation=False, speak_text="ACK.")

        # TIME_QUERY
        if "time" in t and ("what" in t or "tell" in t or t == "time"):
            return KernelResult(intent="TIME_QUERY", confidence=0.95, require_confirmation=False)

        # LED intents (explicit mapping)
        if ("led" in t or "light" in t) and ("on" in t or t == "on"):
            conf = 0.92 if "led" in t else 0.85
            req = conf < self.cfg.confirm_confidence_threshold
            return KernelResult(intent="LED_ON", confidence=conf, require_confirmation=req)

        if ("led" in t or "light" in t) and ("off" in t):
            conf = 0.92 if "led" in t else 0.85
            req = conf < self.cfg.confirm_confidence_threshold
            return KernelResult(intent="LED_OFF", confidence=conf, require_confirmation=req)

        # SLEEP
        if t in {"sleep", "go to sleep", "shutdown"}:
            conf = 0.90
            req = conf < self.cfg.confirm_confidence_threshold
            return KernelResult(intent="SLEEP", confidence=conf, require_confirmation=req)

        # Clarification hook (binding: ask one question max)
        if t in {"what", "huh", "repeat"}:
            return KernelResult(
                intent="UNKNOWN",
                confidence=0.50,
                require_confirmation=False,
                clarification_question="Say the command again.",
            )

        return KernelResult(intent="UNKNOWN", confidence=0.10, require_confirmation=False, speak_text="I didn't catch that.")

    # -------------------------
    # Executor (deterministic; only runs in EXECUTION)
    # -------------------------
    def execute(self, kr: KernelResult) -> str:
        intent = kr.intent
        if intent not in INTENTS:
            return "Error."

        if intent == "PING":
            return "ACK."

        if intent == "TIME_QUERY":
            # Binding: short, single sentence
            return time.strftime("It is %I:%M %p").lstrip("0")

        if intent in {"LED_ON", "LED_OFF"}:
            # If you have hardware_executor.py, we try it; otherwise deterministic stub.
            try:
                from hardware_executor import HardwareExecutor  # type: ignore

                hx = HardwareExecutor()
                cmd = "LED ON" if intent == "LED_ON" else "LED OFF"
                res = hx.execute(cmd)
                # res should already be deterministic ACK/ERR
                return str(res).strip() or "Done."
            except Exception:
                return "Done."

        if intent == "SLEEP":
            # Binding: no long speech
            return "Going to sleep."

        return "Done."


# -------------------------
# Optional CLI (text-only loop)
# -------------------------
def _print_help() -> None:
    print("Demerzel brain_controller.py (text-only)", flush=True)
    print("Commands:", flush=True)
    print("  /wake           -> simulate wake", flush=True)
    print("  /wait N         -> wait N seconds (e.g. /wait 2)", flush=True)
    print("  /quit           -> exit", flush=True)
    print("Anything else is treated as FINAL recognized text.", flush=True)


def main() -> int:
    bc = BrainController()
    _print_help()
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not line:
            bc.tick()
            continue

        if line.startswith("/quit"):
            return 0

        if line.startswith("/wake"):
            bc.on_wake()
            continue

        if line.startswith("/wait"):
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                time.sleep(int(parts[1]))
                bc.tick()
            else:
                print("Usage: /wait N", flush=True)
            continue

        # FINAL text
        bc.on_final_text(line)
        bc.tick()


if __name__ == "__main__":
    raise SystemExit(main())

