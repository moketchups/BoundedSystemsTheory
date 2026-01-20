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
from vision_filter import VisionFilter
from memory_manager import MemoryManager
from router_engine import RouterEngine
from code_analyzer import CodeAnalyzer, RiskLevel

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")
SAMPLE_RATE = 16000
CHUNK = 4096

# Track what Demerzel last said (for echo detection)
last_spoken_text = ""

def is_likely_echo(heard: str, spoken: str) -> bool:
    """Demerzel thinks: Is this input likely my own echo?"""
    if not heard or not spoken:
        return False
    
    heard_words = set(heard.lower().split())
    spoken_words = set(spoken.lower().split())
    
    if len(heard_words) < 3:
        return False
    
    # What fraction of heard words appear in what I just said?
    overlap = len(heard_words & spoken_words)
    ratio = overlap / len(heard_words)
    
    if ratio > 0.5:
        print(f"[SELF-AWARENESS] Echo detected - {overlap}/{len(heard_words)} words match my speech")
        return True
    return False

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

def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """
    Speak text via TTS - COGNITIVE echo handling.
    We remember what we said; is_likely_echo() does the thinking.
    """
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember for cognitive echo detection
    
    # Stop mic while speaking (prevents feedback loop)
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Speak (synchronous - blocks until audio done)
    tts.say(text)
    tts.runAndWait()
    
    # Resume listening immediately - trust cognitive filter
    if stream:
        stream.start_stream()
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done, cognitive filter active")

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
    
    # Initialize memory first
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    
    # Initialize cognitive with memory
    cognitive = MultiModelCognitive(memory_manager=memory)
    router = RouterEngine()
    analyzer = CodeAnalyzer()
    
    # Vision filter for echo suppression
    vision = VisionFilter(motion_threshold=50000, speaking_persist=0.8)
    if vision.start():
        print("[VISION] Lip detection active")
    else:
        print("[VISION] WARNING: Could not start, echo suppression disabled")
        vision = None
    
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
            
            speak(tts, "Yes?", stream, recognizer)
            
            # Get command with longer timeout
            command = transcribe_command(recognizer, stream, timeout=8.0)
            if not command:
                speak(tts, "I didn't hear anything.", stream, recognizer)
                continue
            
            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Store user input in memory
            memory.store_conversation("user", command)
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)
            
            print(f"[COGNITIVE] Intent: {cognitive_output.understood_intent}")
            print(f"[COGNITIVE] Command: {cognitive_output.router_command}")
            
            # Handle clarification requests
            if cognitive_output.needs_clarification:
                speak(tts, cognitive_output.clarification_question, stream, recognizer)
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
                    speak(tts, f"I cannot execute this code. {analysis.reasons[0]}", stream, recognizer)
                    continue
                
                # HIGH_RISK code - requires confirmation
                if analysis.risk_level == RiskLevel.HIGH:
                    speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.", stream, recognizer)
                    
                    confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "yes" not in confirm.lower():
                        speak(tts, "Code execution cancelled.", stream, recognizer)
                        continue
                    
                    speak(tts, "Are you sure? Say I'm sure to proceed.", stream, recognizer)
                    final_confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "sure" not in final_confirm.lower():
                        speak(tts, "Code execution cancelled.", stream, recognizer)
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
                    response = f"Code executed successfully. Result: {output[:100]}"
                    speak(tts, response, stream, recognizer)
                    # Store code execution in memory
                    memory.store_conversation("demerzel", response, 
                                            intent="CODE_EXECUTION",
                                            executed=True)
                else:
                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    response = f"Code execution failed. {error[:100]}"
                    speak(tts, response, stream, recognizer)
                    # Store code error in memory
                    memory.store_conversation("demerzel", response,
                                            intent="CODE_EXECUTION_ERROR",
                                            executed=False)
                

                # Stay awake for follow-up
                # Quick beep to signal "ready for follow-up"
                # User can either speak immediately OR ignore and we go back to wake word mode
                print("[VOICE] Follow-up mode (3 seconds)...")
                
                # SHORT timeout - just 3 seconds, not 5
                follow_up_start = time.time()
                follow_up = ""
                
                while time.time() - follow_up_start < 3.0:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            follow_up = text
                            print(f"[FOLLOW-UP] Heard: '{text}'")
                            break
                
                if follow_up:
                    # Multi-modal self-awareness check
                    human_speaking = vision.is_human_speaking() if vision else False
                    echo_detected = is_likely_echo(follow_up, last_spoken_text)
                    
                    if human_speaking:
                        # Camera sees human talking - trust that
                        print(f"[SELF-AWARENESS] Vision confirms human speaking")
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'"
                    elif echo_detected:
                        # No human lips moving + matches my words = my echo
                        print(f"[SELF-AWARENESS] Echo detected (no human lips), ignoring...")
                        follow_up = ""
                        command = None
                    else:
                        # Doesn't match my words, probably human (camera may have missed)
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'")
                    # Loop back to process this command
                else:
                    print("[VOICE] No follow-up detected, back to wake word mode")
                continue
                time.sleep(0.5)
                follow_up = transcribe_command(recognizer, stream, timeout=4.0)
                if follow_up:
                    command = follow_up
                    # Restart loop with new command
                continue
            
            # Route command through kernel
            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream, recognizer)
                memory.store_conversation("demerzel", cognitive_output.discussion, intent="DISCUSS")
                # Follow-up mode after discuss
                print("[VOICE] Follow-up mode (3 seconds)...")
                follow_up_start = time.time()
                follow_up = ""
                
                while time.time() - follow_up_start < 3.0:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            follow_up = text
                            print(f"[FOLLOW-UP] Heard: '{text}'")
                            break
                
                if follow_up:
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(follow_up, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                        # Reset and keep listening for human
                        follow_up_start = time.time()
                        follow_up = ""
                        continue  # Stay in follow-up mode
                    else:
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'")
                else:
                    print("[VOICE] No follow-up, back to wake word mode")
                    command = None
                continue
            router_output = router.route_text(cognitive_output.router_command)
            
            print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")
            
            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak, stream, recognizer)
                # Store demerzel response
                memory.store_conversation("demerzel", router_output.speak, 
                                        intent=str(router_output.intent),
                                        executed=router_output.did_execute)
            
            # Handle sleep mode
            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()
                memory.clear_working_memory()
                speak(tts, "Going to sleep. Wake me when you need me.", stream, recognizer)
    
    except KeyboardInterrupt:
        print("\n[VOICE] Shutting down...")
    finally:
        if vision:
            vision.stop()
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
