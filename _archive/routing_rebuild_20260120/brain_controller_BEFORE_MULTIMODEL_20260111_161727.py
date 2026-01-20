from __future__ import annotations
import os, sys, time, json, subprocess
from dataclasses import dataclass
from typing import List, Optional
from router_engine import RouterEngine
from hardware_executor import HardwareExecutor, default_config
from cognitive_engine import CognitiveEngine
import numpy as np
from scipy import signal

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
    model_rate: int = 16000
    wake_window_s: float = 8.0
    min_confidence: float = 0.2
    use_cognitive: bool = True

def _env(name: str, default: str) -> str:
    v = os.environ.get(name, "").strip()
    return v or default

CONFIRMATION_KEYWORDS = ["yes", "yeah", "sure", "yep", "okay", "no", "nope", "nah", "i'm sure", "im sure"]

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

def is_confirmation_keyword(text: str) -> bool:
    text = text.strip().lower()
    return any(keyword in text for keyword in CONFIRMATION_KEYWORDS)

def resample_audio(data: bytes, src_rate: int, dst_rate: int) -> bytes:
    """Resample audio data from source rate to destination rate."""
    if src_rate == dst_rate:
        return data
    audio = np.frombuffer(data, dtype=np.int16)
    num_samples = int(len(audio) * dst_rate / src_rate)
    resampled = signal.resample(audio, num_samples)
    return resampled.astype(np.int16).tobytes()

def default_voice_config() -> VoiceConfig:
    return VoiceConfig(
        model_path=_env("DEMERZEL_VOSK_MODEL", "./vosk-model-en-us-0.22"),
        input_device=int(os.environ["DEMERZEL_AUDIO_DEVICE"]) if os.environ.get("DEMERZEL_AUDIO_DEVICE") else None,
        model_rate=16000,
        min_confidence=float(_env("DEMERZEL_MIN_CONFIDENCE", "0.2")),
        use_cognitive=os.environ.get("DEMERZEL_USE_COGNITIVE", "true").lower() == "true",
    )

def run_voice(engine: RouterEngine, cfg: VoiceConfig, cognitive: Optional[CognitiveEngine] = None) -> None:
    import vosk, pyaudio
    if not os.path.isdir(cfg.model_path):
        raise FileNotFoundError(f"Vosk model not found at: {cfg.model_path}")
    
    model = vosk.Model(cfg.model_path)
    rec = vosk.KaldiRecognizer(model, cfg.model_rate)
    rec.SetWords(True)
    
    pa = pyaudio.PyAudio()
    
    # Get device info to check sample rate
    device_info = pa.get_device_info_by_index(cfg.input_device) if cfg.input_device else pa.get_default_input_device_info()
    device_rate = int(device_info['defaultSampleRate'])
    
    print(f"[VOICE] Device rate: {device_rate} Hz, Model rate: {cfg.model_rate} Hz")
    print(f"[VOICE] Min confidence: {cfg.min_confidence}")
    
    if cognitive:
        print(f"[COGNITIVE] Enabled")
    
    stream = pa.open(
        format=pyaudio.paInt16, 
        channels=1, 
        rate=device_rate,
        input=True, 
        frames_per_buffer=4000, 
        input_device_index=cfg.input_device
    )
    stream.start_stream()
    
    awake_until = 0.0
    print("[VOICE] listening... (Ctrl-C to exit)")
    
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            
            # Resample if device rate differs from model rate
            if device_rate != cfg.model_rate:
                data = resample_audio(data, device_rate, cfg.model_rate)
            
            if not rec.AcceptWaveform(data):
                continue
            
            j = json.loads(rec.Result() or "{}")
            text = (j.get("text") or "").strip().lower()
            
            # Calculate average confidence
            result_obj = j.get("result", [])
            if result_obj and isinstance(result_obj, list):
                confidences = [w.get("conf", 0) for w in result_obj if isinstance(w, dict)]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            else:
                avg_confidence = 0
            
            # Reject low confidence or empty text
            if not text or len(text) < 3 or avg_confidence < cfg.min_confidence:
                continue
            
            now = time.time()
            is_awake = now < awake_until
            
            print(f"[HEARD] '{text}' (conf={avg_confidence:.2f}) [awake={is_awake}]")
            
            # Wake word detection
            if now > awake_until:
                if any(w in text for w in engine.wake_aliases):
                    beep()
                    say("Yes?", stream)
                    awake_until = now + cfg.wake_window_s
                continue
            
            # Process command while awake
            # Check if it's a confirmation keyword first (bypass cognitive)
            if is_confirmation_keyword(text):
                print(f"[CONFIRMATION] Bypassing cognitive: '{text}'")
                command = normalize_command(text)
            elif cognitive and cfg.use_cognitive:
                print(f"[COGNITIVE] Processing: '{text}'")
                cog_output = cognitive.process(text)
                print(f"[COGNITIVE] Intent: {cog_output.understood_intent}")
                print(f"[COGNITIVE] Command: {cog_output.router_command}")
                
                if cog_output.needs_clarification:
                    say(cog_output.clarification_question, stream)
                    awake_until = time.time() + cfg.wake_window_s
                    continue
                
                if cog_output.explanation:
                    say(cog_output.explanation, stream)
                
                command = cog_output.router_command
            else:
                command = normalize_command(text)
                print(f"[COMMAND] '{text}' -> '{command}'")
            
            try:
                out = engine.route_text(command)
                print(f"[RESULT] intent={out.intent}, executed={out.did_execute}")
                
                if out.speak:
                    say(out.speak, stream)
                
                if out.sleep_mode:
                    say("Entering sleep.", stream)
                    if cognitive:
                        cognitive.clear_history()
                    return
                
                awake_until = time.time() + cfg.wake_window_s
                
            except Exception as e:
                print(f"[ERROR] {e}")
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\n[VOICE] exit")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    mode = (argv[0] if argv else "voice").lower()
    engine = RouterEngine(
        HardwareExecutor(default_config()),
        wake_aliases=[
            "demerzel", "dam merzel", "dammers", "dammera",
            "dam brazil", "dan merzel",
            "demoiselle", "damn rozelle", "damn or zelle",
            "dam rozelle", "dammers l"
        ]
    )
    if mode == "voice":
        cfg = default_voice_config()
        cognitive = CognitiveEngine() if cfg.use_cognitive else None
        run_voice(engine, cfg, cognitive)
        return 0
    from run_router_repl import main as repl
    repl()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
