#!/usr/bin/env python3
"""
Brain Controller: Voice mode with multi-model cognitive layer
FIXED: Follow-up uses partials, echo filtering, Ctrl-C works
"""

import sys
import time
import json
import signal
from pathlib import Path

import pyaudio
import pyttsx3
from vosk import Model, KaldiRecognizer

from multi_model_cognitive import MultiModelCognitive
from vision_filter import VisionFilter
from memory_manager import MemoryManager
from router_engine import RouterEngine
from code_analyzer import CodeAnalyzer, RiskLevel

VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")
SAMPLE_RATE = 16000
CHUNK = 4096

last_spoken_text = ""
shutdown_requested = False

def signal_handler(sig, frame):
    global shutdown_requested
    print("\n[VOICE] Shutdown requested...")
    shutdown_requested = True

signal.signal(signal.SIGINT, signal_handler)

def is_likely_echo(heard: str) -> bool:
    global last_spoken_text
    if not heard or not last_spoken_text:
        return False
    heard_words = set(heard.lower().split())
    spoken_words = set(last_spoken_text.lower().split())
    if len(heard_words) < 2:
        return False
    overlap = len(heard_words & spoken_words)
    ratio = overlap / len(heard_words)
    if ratio > 0.4:
        print(f"[ECHO] {ratio:.0%} match - ignoring")
        return True
    return False

def init_vosk(model_path: str, sample_rate: int) -> KaldiRecognizer:
    if not Path(model_path).exists():
        print(f"[ERROR] Vosk model not found at: {model_path}")
        sys.exit(1)
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetMaxAlternatives(0)
    recognizer.SetWords(False)
    print(f"[VOICE] Vosk model loaded from {model_path}")
    return recognizer

def init_tts() -> pyttsx3.Engine:
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)
    print("[VOICE] TTS initialized")
    return engine

def init_audio() -> pyaudio.PyAudio:
    p = pyaudio.PyAudio()
    print("[VOICE] PyAudio initialized")
    return p

def get_microphone_stream(p: pyaudio.PyAudio, rate: int, chunk: int):
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
    print(f"[VOICE] Microphone stream opened")
    return stream

def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    tts.say(text)
    tts.runAndWait()
    if stream:
        stream.start_stream()
        time.sleep(0.3)
        try:
            while stream.get_read_available() > 0:
                stream.read(4096, exception_on_overflow=False)
        except:
            pass
    if recognizer:
        recognizer.Reset()
    print("[SPEAK] Done")

def listen_for_wake_word(recognizer: KaldiRecognizer, stream, wake_words: list[str]) -> bool:
    if shutdown_requested:
        return False
    data = stream.read(CHUNK, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()
        if text:
            for wake in wake_words:
                if wake in text:
                    print(f"[HEARD] Wake word: '{text}'")
                    return True
    return False

def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 12.0) -> str:
    print("[COMMAND] Listening...")
    start_time = time.time()
    all_text = []
    last_partial = ""
    partial_stable_since = None
    
    while time.time() - start_time < timeout and not shutdown_requested:
        data = stream.read(CHUNK, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}'")
                all_text.append(text)
                last_partial = ""
                partial_stable_since = None
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text:
                print(f"[PARTIAL] '{partial_text}'")
                if partial_text == last_partial:
                    if partial_stable_since is None:
                        partial_stable_since = time.time()
                    elif time.time() - partial_stable_since >= 2.0:
                        print(f"[STABLE] Accepting partial")
                        all_text.append(partial_text)
                        break
                else:
                    last_partial = partial_text
                    partial_stable_since = time.time()
    
    full_command = " ".join(all_text).strip()
    if not full_command and last_partial and len(last_partial.split()) >= 3:
        print(f"[FALLBACK] Using: '{last_partial}'")
        full_command = last_partial
    if full_command:
        print(f"[COMMAND] '{full_command}'")
    return full_command

def transcribe_followup(recognizer: KaldiRecognizer, stream, timeout: float = 5.0) -> str:
    print(f"[FOLLOW-UP] Listening {timeout}s...")
    start_time = time.time()
    last_partial = ""
    partial_stable_since = None
    
    while time.time() - start_time < timeout and not shutdown_requested:
        data = stream.read(CHUNK, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text and len(text.split()) >= 2:
                if is_likely_echo(text):
                    continue
                print(f"[FOLLOW-UP] Heard: '{text}'")
                return text
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text and len(partial_text.split()) >= 2:
                print(f"[FOLLOW-UP PARTIAL] '{partial_text}'")
                if partial_text == last_partial:
                    if partial_stable_since is None:
                        partial_stable_since = time.time()
                    elif time.time() - partial_stable_since >= 1.5:
                        if is_likely_echo(partial_text):
                            last_partial = ""
                            partial_stable_since = None
                            continue
                        print(f"[FOLLOW-UP STABLE] '{partial_text}'")
                        return partial_text
                else:
                    last_partial = partial_text
                    partial_stable_since = time.time()
    
    if last_partial and len(last_partial.split()) >= 3 and not is_likely_echo(last_partial):
        return last_partial
    return ""

def main_voice_loop():
    global shutdown_requested
    recognizer = init_vosk(VOSK_MODEL_PATH, SAMPLE_RATE)
    tts = init_tts()
    p = init_audio()
    stream = get_microphone_stream(p, SAMPLE_RATE, CHUNK)
    
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    cognitive = MultiModelCognitive(memory_manager=memory)
    router = RouterEngine()
    analyzer = CodeAnalyzer()
    
    vision = VisionFilter(motion_threshold=50000, speaking_persist=0.8)
    if vision.start():
        print("[VISION] Lip detection active")
    else:
        vision = None
    
    wake_words = ["demerzel", "damn brazil", "demoiselle", "dammers l", "d brazil", "de brazil"]
    
    print("\n" + "="*60)
    print("[VOICE] Listening... (Ctrl-C to exit)")
    print("="*60 + "\n")
    
    command = None
    
    try:
        while not shutdown_requested:
            if command is None:
                if not listen_for_wake_word(recognizer, stream, wake_words):
                    continue
                speak(tts, "Yes?", stream, recognizer)
                command = transcribe_command(recognizer, stream)
            
            if not command:
                speak(tts, "I didn't hear anything.", stream, recognizer)
                command = None
                continue
            
            print(f"[PROCESSING] '{command}'")
            memory.store_conversation("user", command)
            cognitive_output = cognitive.process(command)
            print(f"[INTENT] {cognitive_output.understood_intent}")
            print(f"[ROUTE] {cognitive_output.router_command}")
            
            if cognitive_output.needs_clarification:
                speak(tts, cognitive_output.clarification_question, stream, recognizer)
                command = None
                continue
            
            if cognitive_output.router_command == "execute code" and cognitive_output.generated_code:
                code = cognitive_output.generated_code
                print(f"[CODE]\n{code}")
                analysis = analyzer.analyze(code)
                print(f"[RISK] {analysis.risk_level.value}")
                
                if analysis.risk_level == RiskLevel.BLOCKED:
                    speak(tts, f"Cannot execute: {analysis.reasons[0]}", stream, recognizer)
                    command = None
                    continue
                
                if analysis.risk_level == RiskLevel.HIGH:
                    speak(tts, "High risk. Say yes to proceed.", stream, recognizer)
                    confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "yes" not in confirm.lower():
                        speak(tts, "Cancelled.", stream, recognizer)
                        command = None
                        continue
                
                print("[EXEC] Running...")
                result = router.code_executor.execute(code)
                if result.success:
                    lines = [l for l in result.stdout.strip().split("\n") if not l.startswith("[FILE")]
                    output = "\n".join(lines).strip() or "(no output)"
                    print(f"[OUTPUT] {output}")
                    speak(tts, f"Result: {output[:100]}", stream, recognizer)
                else:
                    speak(tts, f"Error: {result.stderr[:100]}", stream, recognizer)
                
                follow_up = transcribe_followup(recognizer, stream, timeout=5.0)
                if follow_up:
                    command = follow_up
                else:
                    print("[VOICE] No follow-up")
                    command = None
                continue
            
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                speak(tts, cognitive_output.discussion, stream, recognizer)
                follow_up = transcribe_followup(recognizer, stream, timeout=5.0)
                if follow_up:
                    command = follow_up
                else:
                    command = None
                continue
            
            router_output = router.route_text(cognitive_output.router_command)
            if router_output.speak:
                speak(tts, router_output.speak, stream, recognizer)
            command = None
    
    finally:
        print("\n[VOICE] Shutting down...")
        if vision:
            vision.stop()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Done")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "voice":
        main_voice_loop()
    else:
        print("Usage: python3 brain_controller.py voice")
