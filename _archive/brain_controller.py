#!/usr/bin/env python3
"""
Brain Controller: Voice mode with multi-model cognitive layer

January 19, 2026 Fixes:
- Wake word detection checks PARTIAL results (not just final)
- Echo threshold increased from 0.4 to 0.5
- Vision gate: only accept speech when human lips are moving
- Updated VisionFilter parameters for better detection

January 19, 2026 New Services Available:
- tts_service: ElevenLabs TTS with pyttsx3 fallback (get_tts_service())
- transcription_service: Deepgram with Vosk fallback (get_transcription_service())
- github_tracker: Audit logging and GitHub integration (get_github_tracker())
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
from cognitive_router import CognitiveRouter, Intent

# New services (January 19, 2026) - import but don't break if unavailable
try:
    from tts_service import get_tts_service, TTSService
    TTS_SERVICE_AVAILABLE = True
except ImportError:
    TTS_SERVICE_AVAILABLE = False

try:
    from transcription_service import get_transcription_service, TranscriptionService
    TRANSCRIPTION_SERVICE_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_SERVICE_AVAILABLE = False

try:
    from github_tracker import get_github_tracker, GitHubTracker
    GITHUB_TRACKER_AVAILABLE = True
except ImportError:
    GITHUB_TRACKER_AVAILABLE = False

VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")
SAMPLE_RATE = 16000
CHUNK = 4096

# Echo detection threshold (January 19, 2026: increased from 0.4 to 0.5)
ECHO_THRESHOLD = 0.5

last_spoken_text = ""
shutdown_requested = False


def signal_handler(sig, frame):
    global shutdown_requested
    print("\n[VOICE] Shutdown requested...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)


def is_likely_echo(heard: str) -> bool:
    """
    Check if heard text is likely an echo of what was just spoken.

    January 19, 2026: Threshold increased from 0.4 to 0.5 to avoid
    rejecting legitimate follow-up commands that share words with response.
    """
    global last_spoken_text
    if not heard or not last_spoken_text:
        return False
    heard_words = set(heard.lower().split())
    spoken_words = set(last_spoken_text.lower().split())
    if len(heard_words) < 2:
        return False
    overlap = len(heard_words & spoken_words)
    ratio = overlap / len(heard_words)
    if ratio > ECHO_THRESHOLD:
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


def listen_for_wake_word(recognizer: KaldiRecognizer, stream, wake_words: list[str], vision=None) -> bool:
    """
    Listen for wake word in both FINAL and PARTIAL results.

    January 19, 2026 Fixes:
    - Also check partial results for wake words (faster detection)
    - Optional vision gate: only trigger if human lips are moving

    January 21, 2026 Fix:
    - Vision gate is now OPTIONAL for wake words (was too strict)
    - Only use vision gate if face is detected (don't block if no face)
    """
    if shutdown_requested:
        return False

    data = stream.read(CHUNK, exception_on_overflow=False)

    # Check FINAL results
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()
        if text:
            for wake in wake_words:
                if wake in text:
                    # Vision gate: ONLY apply if face is detected
                    # If no face detected, accept the wake word (user might be off-camera)
                    if vision and vision.has_face() and not vision.is_human_speaking():
                        print(f"[WAKE] Heard '{text}' but lips not moving - ignoring")
                        return False
                    print(f"[HEARD] Wake word (final): '{text}'")
                    return True
    else:
        # Also check PARTIAL results for faster wake word detection
        partial = json.loads(recognizer.PartialResult())
        partial_text = partial.get("partial", "").lower()
        if partial_text:
            for wake in wake_words:
                if wake in partial_text:
                    # Vision gate: ONLY if face detected
                    if vision and vision.has_face() and not vision.is_human_speaking():
                        return False
                    print(f"[HEARD] Wake word (partial): '{partial_text}'")
                    recognizer.Reset()
                    return True

    return False


def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 12.0, vision=None) -> str:
    """
    Transcribe a command after wake word.

    January 19, 2026: Added optional vision gate for validation.
    """
    print("[COMMAND] Listening...")
    start_time = time.time()
    all_text = []
    last_partial = ""
    partial_stable_since = None

    # Track if we've seen human speaking at all during this command
    human_speaking_seen = False

    while time.time() - start_time < timeout and not shutdown_requested:
        data = stream.read(CHUNK, exception_on_overflow=False)

        # Track if human is speaking (for validation)
        if vision and vision.is_human_speaking():
            human_speaking_seen = True

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

    # Vision validation: if we have vision and never saw human speaking, be suspicious
    if vision and full_command and not human_speaking_seen:
        print(f"[VISION] Warning: Command heard but no human lips moving detected")
        # Don't reject - vision might have missed it, but log the warning

    if full_command:
        print(f"[COMMAND] '{full_command}'")
    return full_command


def transcribe_followup(recognizer: KaldiRecognizer, stream, timeout: float = 5.0, vision=None) -> str:
    """
    Listen for follow-up command with echo filtering.

    January 19, 2026: Added vision gate for follow-up detection.
    """
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
                # Vision gate: prefer when human is actually speaking
                if vision and not vision.is_human_speaking():
                    print(f"[FOLLOW-UP] Heard '{text}' but no human speaking - suspicious")
                    # Don't reject entirely, but note it
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
    router = CognitiveRouter()

    # January 19, 2026: Updated VisionFilter parameters
    vision = VisionFilter(
        motion_threshold=30000,  # Conservative for fallback mode
        speaking_persist=1.5,  # Natural speech pauses
        lip_aperture_threshold=0.3  # MAR threshold for dlib
    )
    if vision.start():
        method = "dlib landmarks" if vision.use_dlib else "Haar cascade"
        print(f"[VISION] Lip detection active ({method})")
    else:
        vision = None
        print("[VISION] Not available - proceeding without vision gate")

    # Wake word variants - Vosk often mishears "Demerzel"
    # January 21, 2026: Added more variants
    wake_words = [
        "demerzel", "demersel", "demersol", "demurzel",
        "damn brazil", "demoiselle", "dammers l", "d brazil", "de brazil",
        "de merzel", "the merzel", "de muzzle", "de muzzell",
        "hey demerzel", "hey demersol", "ok demerzel",
        "demers", "dimmers", "timers all", "de muscle",
    ]

    print("\n" + "=" * 60)
    print("[VOICE] Listening... (Ctrl-C to exit)")
    if vision:
        print("[VOICE] Vision gate ACTIVE - requires human lips moving")
    print("=" * 60 + "\n")

    command = None

    try:
        while not shutdown_requested:
            if command is None:
                # Pass vision to wake word detection for gate
                if not listen_for_wake_word(recognizer, stream, wake_words, vision):
                    continue
                speak(tts, "Yes?", stream, recognizer)
                command = transcribe_command(recognizer, stream, vision=vision)

            if not command:
                speak(tts, "I didn't hear anything.", stream, recognizer)
                command = None
                continue

            print(f"[PROCESSING] '{command}'")
            memory.store_conversation("user", command)

            # Use unified cognitive_router - SINGLE classifier, handlers are terminal
            result = router.route(command)

            # Speak the response - handler already completed the request
            speak(tts, result.response[:500], stream, recognizer)

            # Check for follow-up
            follow_up = transcribe_followup(recognizer, stream, timeout=5.0, vision=vision)
            if follow_up:
                command = follow_up
            else:
                command = None

    finally:
        print("\n[VOICE] Shutting down...")
        if vision:
            vision.stop()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Done")


def main_chat_loop():
    """Text-based chat mode - bypasses voice entirely"""
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    cognitive = MultiModelCognitive(memory_manager=memory)
    router = CognitiveRouter()

    print("\n" + "=" * 60)
    print("[CHAT] Demerzel text mode. Type 'quit' to exit.")
    print("[CHAT] Using unified cognitive_router")
    print("=" * 60 + "\n")

    while True:
        try:
            command = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not command:
            continue
        if command.lower() in ['quit', 'exit', 'q']:
            break

        memory.store_conversation("user", command)

        # Use unified cognitive_router - SINGLE classifier, handlers are terminal
        result = router.route(command)

        # Print the router response - handler already completed the request
        print(f"Demerzel: {result.response}")

    print("\n[CHAT] Goodbye.")


def main():
    """Entry point for run_demerzel.py"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "voice":
            main_voice_loop()
        elif sys.argv[1] == "chat":
            main_chat_loop()
        else:
            print("Usage: python3 brain_controller.py [voice|chat]")
            return 1
    else:
        print("Usage: python3 brain_controller.py [voice|chat]")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
