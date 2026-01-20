from __future__ import annotations
import os, sys, time, json, subprocess
from dataclasses import dataclass
from typing import List, Optional
from router_engine import RouterEngine
from hardware_executor import HardwareExecutor, default_config

def say(text: str, stream=None) -> None:
    if not text:
        return
    if stream:
        stream.stop_stream()
    try:
        subprocess.run(["say", text], check=False)
        time.sleep(0.5)
    except Exception:
        print(f"[SAY] {text}")
    finally:
        if stream:
            stream.start_stream()

def beep() -> None:
    print("\a", end="", flush=True)

@dataclass
class VoiceConfig:
    model_path: str
    input_device: Optional[int] = None
    rate: int = 16000
    wake_window_s: float = 8.0

def _env(name: str, default: str) -> str:
    v = os.environ.get(name, "").strip()
    return v or default

COMMAND_MAP = {
    "link": "ping", "links": "ping", "pink": "ping", "think": "ping",
    "paying": "ping", "peng": "ping", "pings": "ping",
    "lights on": "led on", "light on": "led on", "turn on": "led on",
    "led on": "led on", "max on": "led on",
    "lights off": "led off", "light off": "led off", "turn off": "led off",
    "led off": "led off",
    "sleep mode": "sleep", "go to sleep": "sleep", "good night": "sleep",
}

def normalize_command(text: str) -> str:
    text = text.strip().lower()
    return COMMAND_MAP.get(text, text)

def default_voice_config() -> VoiceConfig:
    return VoiceConfig(
        model_path=_env("DEMERZEL_VOSK_MODEL", "./vosk-model-en-us-0.22"),
        input_device=int(os.environ["DEMERZEL_AUDIO_DEVICE"]) if os.environ.get("DEMERZEL_AUDIO_DEVICE") else None,
        rate=int(_env("DEMERZEL_AUDIO_RATE", "16000")),
    )

def run_voice(engine: RouterEngine, cfg: VoiceConfig) -> None:
    import vosk, pyaudio
    if not os.path.isdir(cfg.model_path):
        raise FileNotFoundError(f"Vosk model not found at: {cfg.model_path}")
    model = vosk.Model(cfg.model_path)
    rec = vosk.KaldiRecognizer(model, cfg.rate)
    rec.SetWords(False)
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=cfg.rate,
                     input=True, frames_per_buffer=8000, input_device_index=cfg.input_device)
    stream.start_stream()
    awake_until = 0.0
    print("[VOICE] listening... (Ctrl-C to exit)")
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if not rec.AcceptWaveform(data):
                continue
            j = json.loads(rec.Result() or "{}")
            text = (j.get("text") or "").strip().lower()
            if not text:
                continue
            now = time.time()
            if now > awake_until:
                if any(w in text for w in engine.wake_aliases):
                    beep()
                    say("Yes?", stream)
                    awake_until = now + cfg.wake_window_s
                continue
            command = normalize_command(text)
            print(f"[COMMAND] '{text}' -> '{command}'")
            out = engine.route_text(command)
            if out.speak:
                say(out.speak, stream)
            if out.sleep_mode:
                say("Entering sleep.", stream)
                return
            awake_until = time.time() + cfg.wake_window_s
    except KeyboardInterrupt:
        print("\n[VOICE] exit")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    mode = (argv[0] if argv else "voice").lower()
    engine = RouterEngine(HardwareExecutor(default_config()),
                         wake_aliases=["demerzel", "dam merzel", "dammers", "dammera",
                                       "dam brazil", "dan merzel",
                                       "demoiselle", "damn rozelle", "damn or zelle",
                                       "dam rozelle", "dammers l"])
    if mode == "voice":
        run_voice(engine, default_voice_config())
        return 0
    from run_router_repl import main as repl
    repl()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
