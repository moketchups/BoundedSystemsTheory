# =========================
# brain_controller.py
# =========================

import os
import sys
import time
import json
import queue
import select
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

# Voice/STT
try:
    import sounddevice as sd
except Exception:
    sd = None

try:
    import vosk
except Exception:
    vosk = None

# Local project imports
from kernel_router import route_text, RouterState, RouterOutput


@dataclass
class WakeResult:
    woke: bool
    phrase: str = ""


class BrainController:
    """
    Demerzel Brain Controller
    - Listens for wake word
    - Captures utterance
    - Routes via kernel_router.route_text()
    - Speaks / acts based on RouterOutput
    """

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.vosk_model_dir = self.base_dir / "vosk-model-small-en-us-0.15"

        # Wake + modes
        self.wake_names = {"demerzel", "demersel", "demersal", "demorzle", "demersel"}
        self.state = "SLEEP"  # SLEEP -> AWAKE
        self.last_wake_ts = 0.0

        # Router state (persistent across turns)
        self.router_state = RouterState()
        # Back-compat: some RouterState versions may not define this field
        if not hasattr(self.router_state, "awaiting_confirmation"):
            self.router_state.awaiting_confirmation = False  # back-compat with older RouterState

        # Audio / STT runtime
        self.sample_rate = 16000
        self.q_audio = queue.Queue()
        self.running = True

        # Vosk model
        if vosk is None:
            raise RuntimeError("vosk not installed. Install with: pip install vosk")
        if not self.vosk_model_dir.exists():
            raise RuntimeError(f"Vosk model not found at: {self.vosk_model_dir}")

        self.model = vosk.Model(str(self.vosk_model_dir))
        self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.rec.SetWords(False)

        # macOS TTS
        self.use_say = (sys.platform == "darwin")

    # ----------------------------
    # TTS
    # ----------------------------
    def speak(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        print(f"[SPEAK] {text}")
        if self.use_say:
            os.system(f'say {json.dumps(text)}')  # json.dumps handles quotes safely
        else:
            # If not macOS, just print for now
            pass

    def beep(self):
        # Optional: quick “ack” beep on wake
        try:
            if self.use_say:
                os.system("printf '\\a'")  # terminal bell
        except Exception:
            pass

    # ----------------------------
    # Audio callback
    # ----------------------------
    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            # keep noisy logs minimal
            pass
        self.q_audio.put(bytes(indata))

    # ----------------------------
    # Wake detection
    # ----------------------------
    def _is_wake(self, text: str) -> bool:
        t = (text or "").lower().strip()
        if not t:
            return False
        # Wake if any wake alias appears as a full token
        tokens = set(t.replace(",", " ").replace(".", " ").split())
        return any(w in tokens for w in self.wake_names)

    def listen_for_wake(self) -> WakeResult:
        """
        Blocks until we detect wake word.
        """
        self.rec.Reset()
        while self.running:
            data = self.q_audio.get()
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result() or "{}")
                txt = (result.get("text") or "").strip()
                if self._is_wake(txt):
                    return WakeResult(True, txt)
            else:
                # partial = json.loads(self.rec.PartialResult() or "{}").get("partial","")
                pass
        return WakeResult(False, "")

    def listen_for_utterance(self, timeout_s: float = 6.0) -> str:
        """
        After wake, listen for a command utterance for up to timeout_s.
        Returns best final text.
        """
        self.rec.Reset()
        t0 = time.time()
        final_txt = ""

        while self.running and (time.time() - t0) < timeout_s:
            data = self.q_audio.get()
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result() or "{}")
                txt = (result.get("text") or "").strip()
                if txt:
                    final_txt = txt
                    break
            else:
                # You can use partial results for UI, but keep it quiet
                pass

        # If we timed out without a final, see if we have a partial
        if not final_txt:
            try:
                partial = json.loads(self.rec.FinalResult() or "{}")
                final_txt = (partial.get("text") or "").strip()
            except Exception:
                final_txt = ""

        return final_txt

    # ----------------------------
    # Main loop
    # ----------------------------
    def run(self):
        if sd is None:
            raise RuntimeError("sounddevice not installed. Install with: pip install sounddevice")

        print("[BrainController] starting audio stream...")
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        ):
            print("[BrainController] ready. say wake name to begin.")
            while self.running:
                # 1) Sleep → wait for wake
                self.state = "SLEEP"
                wake = self.listen_for_wake()
                if not wake.woke:
                    continue

                self.last_wake_ts = time.time()
                self.beep()
                self.speak("Yes?")

                # 2) Awake → capture command
                self.state = "AWAKE"
                cmd = self.listen_for_utterance(timeout_s=6.0)
                cmd = (cmd or "").strip()

                if not cmd:
                    self.speak("I didn't catch that.")
                    continue

                print(f"[HEARD] {cmd}")

                # 3) Route
                out: RouterOutput = route_text(cmd, self.router_state)
                # Router may mutate/replace state
                try:
                    self.router_state = out.new_state or self.router_state
                except Exception:
                    pass

                # Back-compat: if RouterState lacks awaiting_confirmation, force default
                if not hasattr(self.router_state, "awaiting_confirmation"):
                    self.router_state.awaiting_confirmation = False

                # 4) Speak (with a de-dup guard while awaiting confirmation)
                should_speak = True
                try:
                    if getattr(self.router_state, "awaiting_confirmation", False):
                        # Some flows re-emit the same prompt; suppress repeats
                        if (out.speak or "").strip() == (getattr(self.router_state, "last_prompt", "") or "").strip():
                            should_speak = False
                except Exception:
                    pass

                if should_speak:
                    self.speak(out.speak)

                # 5) Optional: remember last prompt for de-dup
                try:
                    if getattr(self.router_state, "awaiting_confirmation", False):
                        setattr(self.router_state, "last_prompt", (out.speak or "").strip())
                except Exception:
                    pass


def main():
    bc = BrainController()
    bc.run()


if __name__ == "__main__":
    main()

