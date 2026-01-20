#!/usr/bin/env python3
"""
Brain Controller: Voice mode with multi-model cognitive layer
Orchestrates: Vosk STT -> Multi-model LLM -> Router -> Hardware -> TTS
"""

import sys
import time
import json
from pathlib import Path

# Audio
import pyaudio
import pyttsx3
from vosk import Model, KaldiRecognizer

# Multi-model cognitive
from multi_model_cognitive import MultiModelCognitive
from memory_manager import MemoryManager
from router_engine import RouterEngine
from code_analyzer import CodeAnalyzer, RiskLevel

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")
SAMPLE_RATE = 16000
CHUNK = 4096

def init_vosk(model_path: str, sample_rate: int) -> KaldiRecognizer:
    """Initialize Vosk speech recognition"""
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
    """Initialize text-to-speech"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)
    print("[VOICE] TTS initialized")
    return engine

def init_audio() -> pyaudio.PyAudio:
    """Initialize PyAudio"""
    p = pyaudio.PyAudio()
    print("[VOICE] PyAudio initialized")
    return p

def get_microphone_stream(p: pyaudio.PyAudio, rate: int, chunk: int):
    """Open microphone stream"""
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )
        print(f"[VOICE] Microphone stream opened (rate={rate} Hz, chunk={chunk})")
        return stream
    except Exception as e:
        print(f"[ERROR] Failed to open microphone: {e}")
        sys.exit(1)

def speak(tts: pyttsx3.Engine, text: str):
    """Speak text via TTS"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    tts.say(text)
    tts.runAndWait()

def listen_for_wake_word(recognizer: KaldiRecognizer, stream, wake_words: list[str]) -> bool:
    """Listen for wake word"""
    data = stream.read(CHUNK, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()
        if text:
            for wake in wake_words:
                if wake in text:
                    print(f"[HEARD] Wake word detected: '{text}'")
                    return True
    return False

def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 8.0) -> str:
    """Transcribe user command with longer timeout and better aggregation"""
    print("[COGNITIVE] Listening for command...")
    start_time = time.time()
    all_text = []
    
    while time.time() - start_time < timeout:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0.0):.2f})")
                all_text.append(text)
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text:
                print(f"[PARTIAL] '{partial_text}'")
    
    # Combine all recognized text
    full_command = " ".join(all_text).strip()
    if full_command:
        print(f"[FULL COMMAND] '{full_command}'")
    return full_command

def main_voice_loop():
    """Main voice interaction loop with multi-model cognitive layer"""
    # Initialize components
    recognizer = init_vosk(VOSK_MODEL_PATH, SAMPLE_RATE)
    tts = init_tts()
    p = init_audio()
    stream = get_microphone_stream(p, SAMPLE_RATE, CHUNK)
    
    # Initialize cognitive and router
    cognitive = MultiModelCognitive()
    router = RouterEngine()
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    analyzer = CodeAnalyzer()
    
    # EXPANDED wake words - user requested variations
    wake_words = [
        # Core
        "demerzel", "de merzel", "demer zel",
        # D + Brazil variants
        "damn brazil", "damn brazile", "dan brazil", "dem brazil", "den brazil",
        "dammers l", "demmers l", "damers l", "demers l",
        # Moiselle variants  
        "demoiselle", "the moiselle", "demolish hell", "demo zel",
        # Other mishears
        "damn or sell", "demersol", "them brazil", "tim brazil", "dim brazil",
        "damer zel", "damozel", "damsel", "damsol", "dem sel", "ten brazil"
    ]
    
    print("\n" + "="*60)
    print("[COGNITIVE] Enabled")
    print("[VOICE] Listening... (Ctrl-C to exit)")
    print(f"[WAKE WORDS] Try: demerzel, damn brazil, demoiselle, dammers l")
    print("="*60 + "\n")
    
    try:
        while True:
            # Wait for wake word
            if not listen_for_wake_word(recognizer, stream, wake_words):
                continue
            
            speak(tts, "Yes?")
            
            # Get command with longer timeout
            command = transcribe_command(recognizer, stream, timeout=8.0)
            if not command:
                speak(tts, "I didn't hear anything.")
                continue
            
            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)
            
            print(f"[COGNITIVE] Intent: {cognitive_output.understood_intent}")
            print(f"[COGNITIVE] Command: {cognitive_output.router_command}")
            
            # Handle clarification requests
            if cognitive_output.needs_clarification:
                speak(tts, cognitive_output.clarification_question)
                continue
            
            # Handle code generation
            if cognitive_output.router_command == "execute code" and cognitive_output.generated_code:
                code = cognitive_output.generated_code
                print(f"[CODE GENERATED]\n{code}")
                
                # Analyze code risk
                analysis = analyzer.analyze(code)
                print(f"[CODE ANALYSIS] Risk: {analysis.risk_level.value}")
                print(f"[CODE ANALYSIS] Reasons: {analysis.reasons}")
                
                # BLOCKED code
                if analysis.risk_level == RiskLevel.BLOCKED:
                    speak(tts, f"I cannot execute this code. {analysis.reasons[0]}")
                    continue
                
                # HIGH_RISK code - requires confirmation
                if analysis.risk_level == RiskLevel.HIGH:
                    speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.")
                    
                    confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "yes" not in confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        continue
                    
                    speak(tts, "Are you sure? Say I'm sure to proceed.")
                    final_confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "sure" not in final_confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        continue
                
                # Execute code
                print("[CODE EXECUTION] Running code...")
                result = router.code_executor.execute(code)
                
                if result.success:
                    # Filter out file system debug messages
                    lines = result.stdout.strip().split("\n")
                    output_lines = [l for l in lines if not l.startswith("[FILE SYSTEM]")]
                    output = "\n".join(output_lines).strip() or "(no output)"
                    print(f"[CODE OUTPUT] {output}")
                    speak(tts, f"Code executed successfully. Result: {output[:100]}")
                else:
                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    speak(tts, f"Code execution failed. {error[:100]}")
                
                continue
            
            # Route command through kernel
            router_output = router.route_text(cognitive_output.router_command)
            
            print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")
            
            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak)
                # Store demerzel response
                memory.store_conversation("demerzel", router_output.speak, 
                                        intent=str(router_output.intent),
                                        executed=router_output.did_execute)
            
            # Handle sleep mode
            if router_output.sleep_mode:
                print("[COGNITIVE] History cleared")
                cognitive.clear_history()
                speak(tts, "Going to sleep. Wake me when you need me.")
    
    except KeyboardInterrupt:
        print("\n[VOICE] Shutting down...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Cleanup complete")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "voice":
        main_voice_loop()
    else:
        print("Usage: python3 brain_controller.py voice")
        sys.exit(1)
