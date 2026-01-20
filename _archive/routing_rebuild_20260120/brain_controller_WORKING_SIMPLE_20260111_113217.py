from __future__ import annotations
import os, sys, time, json, subprocess
from dataclasses import dataclass
from typing import List, Optional
from router_engine import RouterEngine
from hardware_executor import HardwareExecutor, default_config

def say(text: str, stream=None) -> None:
    if not text:
        return
    # Pause stream during speech to prevent feedback
    if stream:
        stream.stop_stream()
    try:
        subprocess.run(["say", text], check=False)
        time.sleep(0.5)  # Brief pause after speech
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

def default_voice_config() -> VoiceConfig:
    return VoiceConfig(
        model_path=_env("DEMERZEL_VOSK_MODEL", "./vosk-model-small-en-us-0.15"),
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
            out = engine.route_text(text)
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
                         wake_aliases=["demerzel", "dam merzel", "dammers", "dammera"])
    if mode == "voice":
        run_voice(engine, default_voice_config())
        return 0
    from run_router_repl import main as repl
    repl()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
