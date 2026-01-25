import time, json, queue, sys, os, re, subprocess
from dataclasses import dataclass

# ---- deps ----
try:
    import sounddevice as sd
except Exception as e:
    print("Missing dependency: sounddevice. Try: pip3 install sounddevice")
    raise
try:
    import vosk
except Exception as e:
    print("Missing dependency: vosk. Try: pip3 install vosk")
    raise

# =========================
# Demerzel Participation Policy (enforced)
# =========================

@dataclass
class Cfg:
    model_path: str = "vosk-model-small-en-us-0.15"
    samplerate: int = 16000
    wake_threshold: float = 0.62           # match your logs
    command_window_s: float = 3.0
    confirm_window_s: float = 3.0
    post_say_gate_s: float = 1.4           # key: ignore self-echo after ANY speech
    debug: bool = True                     # prints only; NEVER spoken

CFG = Cfg()

# ---- Intent set (binding) ----
INTENTS = {"PING","LED_ON","LED_OFF","TIME_QUERY","SLEEP","UNKNOWN"}

YES_SET = {"yes","yeah","yep","yup","y","confirm","ok","okay"}
NO_SET  = {"no","nope","n","cancel","stop"}

def clean(t: str) -> str:
    t = (t or "").strip().lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def now_time_string():
    return time.strftime("%I:%M %p").lstrip("0")

def say(text: str):
    # Speech Output Surface: ONLY here
    # Keep it short.
    if not text:
        return
    try:
        subprocess.run(["say", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def beep():
    # Minimal wake ack option; use a short terminal bell
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass

def run_tool(intent: str) -> str:
    # Executor: deterministic mappings only
    # Uses your existing hardware_executor.py if present.
    if intent == "PING":
        if os.path.exists("hardware_executor.py"):
            r = subprocess.run(["python3","hardware_executor.py","PING"], capture_output=True, text=True)
            out = (r.stdout or "").strip()
            return out if out else ("ERR" if r.returncode else "ACK")
        return "ACK"
    if intent == "LED_ON":
        if os.path.exists("hardware_executor.py"):
            r = subprocess.run(["python3","hardware_executor.py","LED_ON"], capture_output=True, text=True)
            return (r.stdout or "").strip() or ("ERR" if r.returncode else "ACK")
        return "ACK"
    if intent == "LED_OFF":
        if os.path.exists("hardware_executor.py"):
            r = subprocess.run(["python3","hardware_executor.py","LED_OFF"], capture_output=True, text=True)
            return (r.stdout or "").strip() or ("ERR" if r.returncode else "ACK")
        return "ACK"
    if intent == "TIME_QUERY":
        return now_time_string()
    if intent == "SLEEP":
        return "OK"
    return "ERR"

def classify(cmd: str) -> str:
    # Router: proposes only, no execution
    c = clean(cmd)

    if not c:
        return "UNKNOWN"

    # time
    if "time" in c:
        return "TIME_QUERY"

    # ping
    if c in {"ping","test ping"} or "ping" in c:
        return "PING"

    # led
    if ("led" in c) or ("light" in c):
        if ("off" in c) or ("turn off" in c):
            return "LED_OFF"
        if ("on" in c) or ("turn on" in c):
            return "LED_ON"

    # sleep
    if c in {"sleep","go to sleep","shutdown"} or ("go to sleep" in c):
        return "SLEEP"

    return "UNKNOWN"

def requires_confirmation(intent: str) -> bool:
    # Binding rule from your policy
    if intent in {"PING","TIME_QUERY"}:
        return False
    if intent in {"LED_ON","LED_OFF","SLEEP"}:
        return True
    return False

def wake_alias_score(text: str) -> float:
    """
    Simple alias scoring: detect "demerzel" + fuzzy split variants.
    We treat:
      - "demerzel"
      - "dam er zel"
      - "dam erzel"
      - "dam braz(il)" (your real-world alias)
    as wake.
    """
    t = clean(text)
    if not t:
        return 0.0
    if "demerzel" in t:
        return 0.95
    # common mishears from your logs
    if "dam er zel" in t or "dam erzel" in t:
        return 0.85
    if "dam brazil" in t or "dam braz" in t:
        return 0.90
    # partial
    if "dem" in t and "zel" in t:
        return 0.70
    return 0.0

class Audio:
    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.q = queue.Queue()
        self.rec = None
        self.model = None
        self.stream = None
        self.mic_gate_until = 0.0

    def start(self):
        if not os.path.isdir(self.cfg.model_path):
            raise SystemExit(f"Missing Vosk model folder: {self.cfg.model_path}")
        self.model = vosk.Model(self.cfg.model_path)
        self.rec = vosk.KaldiRecognizer(self.model, self.cfg.samplerate)
        self.rec.SetWords(True)

        def cb(indata, frames, time_info, status):
            if status:
                return
            self.q.put(bytes(indata))

        self.stream = sd.RawInputStream(
            samplerate=self.cfg.samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=cb,
        )
        self.stream.start()

    def reset_recognizer(self):
        # Hard reset prevents buffered self-echo from resurfacing
        self.rec = vosk.KaldiRecognizer(self.model, self.cfg.samplerate)
        self.rec.SetWords(True)

    def flush_audio(self, duration_s: float = 0.25):
        # Drain queue quickly for a short duration
        end = time.time() + duration_s
        while time.time() < end:
            try:
                self.q.get_nowait()
            except queue.Empty:
                time.sleep(0.01)

    def gate_after_say(self):
        self.mic_gate_until = max(self.mic_gate_until, time.time() + float(self.cfg.post_say_gate_s))
        self.flush_audio(0.35)
        self.reset_recognizer()

    def read_final_until(self, deadline: float):
        # Returns FINAL strings only, no partials
        while time.time() < deadline:
            data = self.q.get()
            if time.time() < self.mic_gate_until:
                continue
            if self.rec.AcceptWaveform(data):
                try:
                    j = json.loads(self.rec.Result() or "{}")
                except Exception:
                    j = {}
                txt = (j.get("text") or "").strip()
                if txt:
                    return txt
        return ""

def main():
    a = Audio(CFG)
    a.start()

    STATE = "IDLE"
    pending_intent = None

    print("[READY] Say 'demerzel' to wake. Ctrl+C to exit.")
    try:
        while True:
            if STATE == "IDLE":
                # Wake detector ON only here
                txt = a.read_final_until(time.time() + 3600)
                score = wake_alias_score(txt)
                if score >= CFG.wake_threshold:
                    if CFG.debug:
                        print(f"[WAKE] detected alias='{txt}' score={score:.2f}")
                    STATE = "WAKE_ACK"
                else:
                    # stay silent
                    continue

            if STATE == "WAKE_ACK":
                # Ack Output ON only here
                # Choose ONE minimal ack: beep + "Yes"
                beep()
                say("Yes")
                a.gate_after_say()  # critical: prevents self-echo becoming a command
                STATE = "COMMAND_WINDOW"
                cmd_deadline = time.time() + CFG.command_window_s
                if CFG.debug:
                    print(f"[STATE] COMMAND_WINDOW ({CFG.command_window_s:.1f}s)")

            if STATE == "COMMAND_WINDOW":
                # STT ON only here
                cmd = a.read_final_until(cmd_deadline)
                if not cmd:
                    if CFG.debug:
                        print("[STATE] command timeout -> IDLE")
                    STATE = "IDLE"
                    continue

                intent = classify(cmd)
                if intent not in INTENTS:
                    intent = "UNKNOWN"

                if CFG.debug:
                    print(f"[FINAL] {cmd}")
                    print(f"[ROUTER] intent={intent}")

                # Unknown => one short clarification then back to IDLE (silent success)
                if intent == "UNKNOWN":
                    say("Say one of: ping, led on, led off, time, sleep.")
                    a.gate_after_say()
                    STATE = "IDLE"
                    continue

                # No-confirm intents execute immediately
                if not requires_confirmation(intent):
                    STATE = "EXECUTION"
                    pending_intent = intent
                else:
                    STATE = "CONFIRMATION_PENDING"
                    pending_intent = intent
                    say(f"I heard {intent.replace('_',' ').lower()}. Confirm? Yes or no.")
                    a.gate_after_say()
                    confirm_deadline = time.time() + CFG.confirm_window_s
                    continue

            if STATE == "CONFIRMATION_PENDING":
                # Only interpret yes/no here
                ans = a.read_final_until(confirm_deadline)
                tok = clean(ans)

                if CFG.debug and ans:
                    print(f"[FINAL] {ans}")

                if not ans:
                    # timeout -> IDLE
                    STATE = "IDLE"
                    pending_intent = None
                    continue

                if tok in YES_SET:
                    STATE = "EXECUTION"
                elif tok in NO_SET:
                    say("Canceled.")
                    a.gate_after_say()
                    STATE = "IDLE"
                    pending_intent = None
                    continue
                else:
                    # One reprompt, still bounded
                    say("Yes or no?")
                    a.gate_after_say()
                    confirm_deadline = time.time() + 1.5
                    continue

            if STATE == "EXECUTION":
                intent = pending_intent or "UNKNOWN"
                if CFG.debug:
                    print(f"[EXEC] {intent}")
                result = run_tool(intent)

                STATE = "RESPONSE"
                # Response Generator ON only here (one sentence)
                if intent == "TIME_QUERY":
                    say(f"It is {result}.")
                elif intent == "SLEEP":
                    say("Going to sleep.")
                    a.gate_after_say()
                    break
                elif result.startswith("ERR"):
                    say("Error.")
                else:
                    say("Done.")
                a.gate_after_say()
                STATE = "IDLE"
                pending_intent = None

    except KeyboardInterrupt:
        print("\n[EXIT]")

if __name__ == "__main__":
    main()
