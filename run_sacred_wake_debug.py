import time, json, queue, sys, os, re, subprocess
from dataclasses import dataclass

import sounddevice as sd
import vosk

@dataclass
class Cfg:
    model_path: str = "vosk-model-small-en-us-0.15"
    samplerate: int = 16000
    wake_threshold: float = 0.50      # LOWER so it wakes while we debug
    command_window_s: float = 3.0
    confirm_window_s: float = 3.0
    post_say_gate_s: float = 1.4
    debug: bool = True               # PRINTS ONLY (never spoken)

CFG = Cfg()

YES_SET = {"yes","yeah","yep","yup","y","confirm","ok","okay"}
NO_SET  = {"no","nope","n","cancel","stop"}

def clean(t: str) -> str:
    t = (t or "").strip().lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def say(text: str):
    if not text:
        return
    try:
        subprocess.run(["say", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def beep():
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass

def now_time_string():
    return time.strftime("%I:%M %p").lstrip("0")

def wake_alias_score(text: str) -> float:
    t = clean(text)
    if not t:
        return 0.0
    # Accept a wider set while debugging
    if "demerzel" in t:
        return 0.95
    if "dam er zel" in t or "dam erzel" in t:
        return 0.85
    if "dam ezel" in t or "dam ezell" in t or "dam ezl" in t:
        return 0.80
    if "dam brazil" in t or "dam braz" in t:
        return 0.90
    if ("dem" in t and "zel" in t) or ("dam" in t and "zel" in t):
        return 0.70
    return 0.0

def classify(cmd: str) -> str:
    c = clean(cmd)
    if not c:
        return "UNKNOWN"
    if "time" in c:
        return "TIME_QUERY"
    if "ping" in c:
        return "PING"
    if ("led" in c) or ("light" in c):
        if "off" in c:
            return "LED_OFF"
        if "on" in c:
            return "LED_ON"
    if c in {"sleep","go to sleep","shutdown"} or ("go to sleep" in c):
        return "SLEEP"
    return "UNKNOWN"

def requires_confirmation(intent: str) -> bool:
    if intent in {"PING","TIME_QUERY"}:
        return False
    if intent in {"LED_ON","LED_OFF","SLEEP"}:
        return True
    return False

def run_tool(intent: str) -> str:
    if intent == "TIME_QUERY":
        return now_time_string()
    if intent == "SLEEP":
        return "OK"
    # If you have hardware_executor.py, it will run; otherwise ACK
    if os.path.exists("hardware_executor.py") and intent in {"PING","LED_ON","LED_OFF"}:
        r = subprocess.run(["python3","hardware_executor.py", intent], capture_output=True, text=True)
        out = (r.stdout or "").strip()
        return out if out else ("ERR" if r.returncode else "ACK")
    return "ACK"

class Audio:
    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.q = queue.Queue()
        self.model = None
        self.rec = None
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
        self.rec = vosk.KaldiRecognizer(self.model, self.cfg.samplerate)
        self.rec.SetWords(True)

    def flush_audio(self, duration_s: float = 0.25):
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

    print("[READY] Say 'demerzel' to wake. (PAUSE after saying it) Ctrl+C to exit.")

    try:
        while True:
            if STATE == "IDLE":
                txt = a.read_final_until(time.time() + 3600)
                score = wake_alias_score(txt)

                # DEBUG: show exactly what Vosk heard
                print(f"[IDLE FINAL] '{txt}'  wake_score={score:.2f}")

                if score >= CFG.wake_threshold:
                    print(f"[WAKE] accepted '{txt}'")
                    STATE = "WAKE_ACK"
                else:
                    continue

            if STATE == "WAKE_ACK":
                beep()
                say("Yes")
                a.gate_after_say()
                STATE = "COMMAND_WINDOW"
                cmd_deadline = time.time() + CFG.command_window_s
                print(f"[STATE] COMMAND_WINDOW ({CFG.command_window_s:.1f}s)")

            if STATE == "COMMAND_WINDOW":
                cmd = a.read_final_until(cmd_deadline)
                if not cmd:
                    print("[STATE] command timeout -> IDLE")
                    STATE = "IDLE"
                    continue

                intent = classify(cmd)
                print(f"[FINAL] {cmd}")
                print(f"[ROUTER] intent={intent}")

                if intent == "UNKNOWN":
                    say("Say one of: ping, led on, led off, time, sleep.")
                    a.gate_after_say()
                    STATE = "IDLE"
                    continue

                if not requires_confirmation(intent):
                    pending_intent = intent
                    STATE = "EXECUTION"
                else:
                    pending_intent = intent
                    STATE = "CONFIRMATION_PENDING"
                    say(f"I heard {intent.replace('_',' ').lower()}. Confirm? Yes or no.")
                    a.gate_after_say()
                    confirm_deadline = time.time() + CFG.confirm_window_s
                    continue

            if STATE == "CONFIRMATION_PENDING":
                ans = a.read_final_until(confirm_deadline)
                tok = clean(ans)
                if ans:
                    print(f"[FINAL] {ans}")

                if not ans:
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
                    say("Yes or no?")
                    a.gate_after_say()
                    confirm_deadline = time.time() + 1.5
                    continue

            if STATE == "EXECUTION":
                intent = pending_intent or "UNKNOWN"
                print(f"[EXEC] {intent}")
                result = run_tool(intent)

                if intent == "TIME_QUERY":
                    say(f"It is {result}.")
                elif intent == "SLEEP":
                    say("Going to sleep.")
                    a.gate_after_say()
                    break
                elif str(result).startswith("ERR"):
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
