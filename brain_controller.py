#!/usr/bin/env python3
import argparse
import json
import queue
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

import pyaudio
from rapidfuzz import fuzz
from vosk import Model, KaldiRecognizer

from router_engine import RouterEngine  # <-- authoritative routing (kernel/router inside)


# -----------------------------
# Helpers
# -----------------------------

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def say_mac(text: str):
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

def beep():
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass

def clean_text(s: str) -> str:
    # Minimal deterministic normalization for wake/echo checks.
    return " ".join((s or "").strip().lower().split())


# -----------------------------
# Audio + Vosk
# -----------------------------

@dataclass
class Config:
    model_path: str
    device_index: int
    wake_threshold: float
    sample_rate: int = 16000
    frame_ms: int = 40

    # windows (seconds)
    command_window: float = 7.0

    # echo protection
    anti_echo_window: float = 1.2
    tts_mic_gate_seconds: float = 1.0

    # NEW: post-wake gating (prevents premature UNKNOWN before user speaks)
    post_wake_cooldown_seconds: float = 0.70   # ignore FINALs briefly after wake+ack
    suppress_clarify_after_wake_seconds: float = 1.20  # don't speak CLARIFY immediately after wake

    # NEW: ignore ultra-short finals in COMMAND mode (except yes/no)
    min_final_chars_command: int = 3


class BrainController:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.model = Model(cfg.model_path)
        self.rec = KaldiRecognizer(self.model, cfg.sample_rate)
        self.audio = pyaudio.PyAudio()
        self.stream = None

        # Deterministic state machine (voice shell only)
        self.state = "IDLE"  # IDLE -> COMMAND
        self.state_deadline = 0.0

        # NEW: gates around wake->command transition
        self.command_gate_until = 0.0          # ignore FINALs until this time
        self.no_clarify_until = 0.0            # don't speak CLARIFY until this time

        # Wake matching
        self.wake_name = "DEMERZEL"
        self.wake_aliases = [
            "demerzel",
            "demerzel.",
            "damerzel",
            "demersel",
            "dam er zel",
            "dammers",
            "dammerzle",
            "dam ezell",
            "dam ezel",
            "dam brazil",
            "dam ezzel",
        ]

        # Anti-echo + mic gate
        self.last_tts_text = ""
        self.last_tts_time = 0.0
        self.mic_gate_until = 0.0

        # Audio queue
        self.q = queue.Queue()

        # Authoritative router engine (holds confirmation state internally)
        self.engine = RouterEngine(high_conf_threshold=0.85)

    # -----------------------------
    # Audio device helpers
    # -----------------------------

    def list_devices(self):
        print("\n=== INPUT DEVICES ===")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if int(info.get("maxInputChannels", 0)) > 0:
                print(
                    f"[{i}] ch={int(info.get('maxInputChannels', 0))} "
                    f"sr={int(info.get('defaultSampleRate', 0))} "
                    f"name={info.get('name')}"
                )
        print("=== END ===\n")

    def _open_stream(self):
        frame = int(self.cfg.sample_rate * (self.cfg.frame_ms / 1000.0))

        def callback(in_data, frame_count, time_info, status_flags):
            self.q.put(in_data)
            return (None, pyaudio.paContinue)

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.cfg.sample_rate,
            input=True,
            input_device_index=self.cfg.device_index,
            frames_per_buffer=frame,
            stream_callback=callback,
        )
        self.stream.start_stream()
        print(f"[AUDIO] device={self.cfg.device_index} channels=1 sr={self.cfg.sample_rate} frame={frame}")

    def close(self):
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass
        try:
            self.audio.terminate()
        except Exception:
            pass

    def _flush_audio_queue(self, max_chunks: int = 999):
        n = 0
        try:
            while n < max_chunks:
                self.q.get_nowait()
                n += 1
        except Exception:
            pass
        if n:
            print(f"[GATE] Flushed {n} audio chunks.")

    # -----------------------------
    # Speech output with anti-echo tracking + mic gate
    # -----------------------------

    def say(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        print(f"[SAY] {text}")

        self.last_tts_text = clean_text(text)
        self.last_tts_time = time.time()
        self.mic_gate_until = time.time() + float(self.cfg.tts_mic_gate_seconds)

        say_mac(text)

        # Flush & reset recognizer to reduce TTS echo pickup
        self._flush_audio_queue()
        try:
            self.rec.Reset()
            print("[GATE] Vosk recognizer reset.")
        except Exception:
            pass

    def _anti_echo_should_ignore(self, final_text: str) -> bool:
        ft = clean_text(final_text)
        if not ft or not self.last_tts_text:
            return False
        if time.time() - self.last_tts_time > self.cfg.anti_echo_window:
            return False
        if ft == self.last_tts_text:
            print("[ANTI-ECHO] Ignored exact match to last TTS.")
            return True
        return False

    # -----------------------------
    # Wake logic
    # -----------------------------

    def _wake_score(self, heard: str) -> Tuple[str, float]:
        h = clean_text(heard)
        best = ("", 0.0)
        for a in self.wake_aliases:
            s = fuzz.partial_ratio(h, clean_text(a)) / 100.0
            if s > best[1]:
                best = (a, s)
        return best

    def _strip_wake_alias(self, final_text: str, best_alias: str) -> str:
        """
        Deterministically remove the best-matching alias from the utterance once.
        Conservative: only strips if the alias appears as a substring after normalization.
        """
        t = clean_text(final_text)
        a = clean_text(best_alias)
        if not a:
            return final_text

        if a in t:
            out = t.replace(a, "", 1).strip()
            return out
        return final_text

    # -----------------------------
    # State
    # -----------------------------

    def _enter_command_state(self):
        self.state = "COMMAND"
        self.state_deadline = time.time() + self.cfg.command_window

        # NEW: after wake, ignore the next brief burst of FINALs (noise/tail)
        now = time.time()
        self.command_gate_until = max(self.command_gate_until, now + float(self.cfg.post_wake_cooldown_seconds))
        self.no_clarify_until = max(self.no_clarify_until, now + float(self.cfg.suppress_clarify_after_wake_seconds))

        print(f"[STATE] COMMAND ({int(self.cfg.command_window)}s left)")
        print(f"[GATE] command_gate_until={self.command_gate_until:.2f} (now={now:.2f})")
        print(f"[GATE] no_clarify_until={self.no_clarify_until:.2f} (now={now:.2f})")

    def _back_to_idle(self):
        self.state = "IDLE"
        self.state_deadline = 0.0
        self.command_gate_until = 0.0
        self.no_clarify_until = 0.0
        print("[STATE] IDLE")

    # -----------------------------
    # Router output selection (what to speak)
    # -----------------------------

    def _choose_speak_line(self, lines: List[str]) -> Optional[str]:
        """
        Deterministic rule: pick the highest-priority line to speak.
        Priority (first match wins, from bottom-most occurrence):
          1) Confirmation prompt
          2) CLARIFY:
          3) ERROR:
          4) HARDWARE:
        Otherwise: speak nothing.
        """
        if not lines:
            return None

        # scan from bottom up to speak the latest relevant line
        for line in reversed(lines):
            if "Confirm?" in line or line.strip().lower().startswith("confirm"):
                return line.strip()
        for line in reversed(lines):
            if line.startswith("CLARIFY:"):
                return line.replace("CLARIFY:", "").strip()
        for line in reversed(lines):
            if line.startswith("ERROR:"):
                return line.strip()
        for line in reversed(lines):
            if line.startswith("HARDWARE:"):
                return line.replace("HARDWARE:", "").strip()

        return None

    def _is_yes_no(self, s: str) -> bool:
        t = clean_text(s)
        return t in {"yes", "no", "y", "n"}

    # -----------------------------
    # Main loop
    # -----------------------------

    def run(self):
        self._open_stream()

        print(f"[READY] Say '{self.wake_aliases[0]}' to wake. Ctrl+C to exit.")
        print(f"[WINDOW] command={self.cfg.command_window}s")
        print(f"[WAKE] threshold={self.cfg.wake_threshold:.2f}")
        print(f"[GATE] tts_mic_gate_seconds={self.cfg.tts_mic_gate_seconds:.2f}s")
        print(f"[GATE] post_wake_cooldown_seconds={self.cfg.post_wake_cooldown_seconds:.2f}s")
        print(f"[GATE] min_final_chars_command={self.cfg.min_final_chars_command}")

        try:
            while True:
                # Timeout state window
                if self.state != "IDLE" and time.time() > self.state_deadline:
                    print("[STATE] window timeout -> IDLE")
                    self._back_to_idle()

                data = self.q.get()

                # Mic gate during TTS
                if time.time() < self.mic_gate_until:
                    continue

                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result() or "{}")
                    text = (result.get("text") or "").strip()
                    if not text:
                        continue

                    final_text = text
                    print(f"[FINAL] {final_text}")

                    if self._anti_echo_should_ignore(final_text):
                        continue

                    best_alias, score = self._wake_score(final_text)
                    wake_detected = (score >= self.cfg.wake_threshold)

                    # --- IDLE: only wake transitions are allowed ---
                    if self.state == "IDLE":
                        if not wake_detected:
                            continue

                        print(f"[WAKE] detected alias='{best_alias}' score={score:.2f}")
                        beep()
                        self.say("Yes?")

                        # Enter command mode with post-wake gating
                        self._enter_command_state()

                        # If user said wake + command in same utterance, strip and try once.
                        remainder = self._strip_wake_alias(final_text, best_alias).strip()

                        # Only route remainder if it's not empty and not just the wake alias.
                        if remainder and remainder != clean_text(best_alias):
                            # NOTE: remainder is from the same utterance as wake (safe to process immediately)
                            print(f"[WAKE] remainder -> '{remainder}'")
                            lines = self.engine.process(remainder)
                            for ln in lines:
                                print(ln)

                            speak = self._choose_speak_line(lines)
                            if speak:
                                # Allow confirmation prompts immediately; suppress CLARIFY during no_clarify_until
                                if speak.lower().startswith("i’m not sure") or speak.lower().startswith("im not sure"):
                                    # treat as clarify
                                    if time.time() >= self.no_clarify_until:
                                        self.say(speak)
                                    else:
                                        print("[GATE] Suppressed immediate CLARIFY after wake (remainder path).")
                                else:
                                    self.say(speak)

                        continue

                    # --- COMMAND: route final utterances into authoritative router (with gates) ---
                    if self.state == "COMMAND":
                        now = time.time()

                        # NEW: post-wake cooldown gate prevents premature UNKNOWN
                        if now < self.command_gate_until:
                            print("[GATE] Ignored FINAL during post-wake cooldown.")
                            continue

                        # NEW: ignore ultra-short finals unless they are yes/no (for confirmation)
                        if (len(clean_text(final_text)) < self.cfg.min_final_chars_command) and (not self._is_yes_no(final_text)):
                            print("[GATE] Ignored very short FINAL in COMMAND mode.")
                            continue

                        lines = self.engine.process(final_text)
                        for ln in lines:
                            print(ln)

                        speak = self._choose_speak_line(lines)
                        if speak:
                            # NEW: suppress speaking CLARIFY immediately after wake (but still print it)
                            if now < self.no_clarify_until:
                                # If it's a clarify, suppress it; confirmations/errors/hardware can still speak
                                if speak.lower().startswith("i’m not sure") or speak.lower().startswith("im not sure"):
                                    print("[GATE] Suppressed immediate CLARIFY after wake.")
                                else:
                                    self.say(speak)
                            else:
                                self.say(speak)

                        continue

                else:
                    pres = json.loads(self.rec.PartialResult() or "{}")
                    p = (pres.get("partial") or "").strip()
                    if p and len(p) < 60:
                        print(f"[partial] {p}")

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C received. Exiting cleanly...")
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true", help="List input devices and exit")
    parser.add_argument("--device", type=int, default=0, help="Input device index")
    parser.add_argument("--model", type=str, default="vosk-model-small-en-us-0.15", help="Path to Vosk model dir")
    parser.add_argument("--wake-threshold", type=float, default=0.62, help="Wake match threshold (0-1)")
    args = parser.parse_args()

    cfg = Config(
        model_path=args.model,
        device_index=args.device,
        wake_threshold=args.wake_threshold,
    )

    bc = BrainController(cfg)
    if args.list_devices:
        bc.list_devices()
        return
    bc.run()


if __name__ == "__main__":
    main()

