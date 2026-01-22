#!/usr/bin/env python3
"""
run_demerzel.py - Entry Point

R -> C -> I Architecture:
Single entry point for Demerzel.
Voice mode or text mode, state-driven.

Usage:
    python3 run_demerzel.py          # Voice mode (default)
    python3 run_demerzel.py voice    # Voice mode
    python3 run_demerzel.py text     # Text mode (REPL)

CRITICAL: During SPEAKING state, transcription is BLOCKED.
This is STRUCTURAL selftalk prevention.
"""

import sys
import time
import json
import signal
from pathlib import Path

from demerzel_core import Demerzel, DemerzelState, get_demerzel


# =============================================================================
# GLOBALS
# =============================================================================

shutdown_requested = False
WAKE_WORDS = ["demerzel", "the merzel", "hey merzel", "ok merzel", "denver", "de merzel", "demers", "d merzel"]


def signal_handler(sig, frame):
    global shutdown_requested
    print("\n[MAIN] Shutdown requested...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)


# =============================================================================
# SERVICE INITIALIZATION
# =============================================================================

def init_services():
    """Initialize optional services with graceful fallbacks."""
    services = {}

    # Memory Manager
    try:
        from memory_manager import MemoryManager
        services['memory'] = MemoryManager()
        print("[INIT] Memory manager: OK")
    except Exception as e:
        print(f"[INIT] Memory manager: FAILED - {e}")
        services['memory'] = None

    # Hardware Executor
    try:
        from hardware_executor import HardwareExecutor
        services['hardware'] = HardwareExecutor()
        print("[INIT] Hardware executor: OK")
    except Exception as e:
        print(f"[INIT] Hardware executor: FAILED - {e}")
        services['hardware'] = None

    # TTS Service
    try:
        from tts_service import get_tts_service
        services['tts'] = get_tts_service()
        print("[INIT] TTS service: OK")
    except Exception as e:
        print(f"[INIT] TTS service: FAILED - {e}")
        services['tts'] = None

    # Transcription Service
    try:
        from transcription_service import get_transcription_service
        services['transcriber'] = get_transcription_service()
        print("[INIT] Transcription service: OK")
    except Exception as e:
        print(f"[INIT] Transcription service: FAILED - {e}")
        services['transcriber'] = None

    return services


# =============================================================================
# TEXT MODE (REPL)
# =============================================================================

def text_loop(demerzel: Demerzel):
    """
    Text mode REPL.
    Input -> Process -> Output
    """
    print("\n" + "=" * 60)
    print("DEMERZEL TEXT MODE")
    print("=" * 60)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'status' to see system status")
    print("-" * 60)

    while not shutdown_requested:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        if not user_input:
            continue

        # Check for exit commands
        if user_input.lower() in ('quit', 'exit', 'q'):
            print("\nDemerzel: Goodbye.")
            break

        # Check for status command
        if user_input.lower() == 'status':
            print("\nStatus:")
            for key, value in demerzel.get_status().items():
                print(f"  {key}: {value}")
            continue

        # Process through Demerzel
        response = demerzel.process(user_input)
        print(f"\nDemerzel: {response}")

        # Store in memory if available
        if demerzel.memory:
            try:
                demerzel.memory.store_conversation("user", user_input)
                demerzel.memory.store_conversation("demerzel", response)
            except:
                pass

    print("\n[TEXT] Session ended")


# =============================================================================
# VOICE MODE
# =============================================================================

def voice_loop(demerzel: Demerzel):
    """
    State-driven voice loop.
    IDLE -> LISTENING -> PROCESSING -> SPEAKING -> IDLE

    CRITICAL: Transcription is BLOCKED during SPEAKING state.
    This is structural selftalk prevention, not timing hacks.
    """
    import pyaudio
    from vosk import Model, KaldiRecognizer
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print("\n" + "=" * 60)
    print("DEMERZEL VOICE MODE")
    print("=" * 60)

    # Initialize audio constants
    SAMPLE_RATE = 16000
    CHUNK = 4096
    VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")

    if not Path(VOSK_MODEL_PATH).exists():
        print(f"[VOICE] ERROR: Vosk model not found at {VOSK_MODEL_PATH}")
        print("[VOICE] Falling back to text mode")
        return text_loop(demerzel)

    # =================================================================
    # PARALLEL LOADING: Vosk + VisionFilter load concurrently
    # =================================================================
    print("[VOICE] Loading models in parallel...")
    load_start = time.time()

    model = None
    vision = None
    vosk_error = None
    vision_error = None

    def load_vosk():
        """Load Vosk model (heavy)."""
        nonlocal model, vosk_error
        try:
            model = Model(VOSK_MODEL_PATH)
            print(f"[VOICE] Vosk model loaded ({time.time() - load_start:.1f}s)")
        except Exception as e:
            vosk_error = e
            print(f"[VOICE] Vosk init failed: {e}")

    def load_vision():
        """Load VisionFilter with dlib (heavy)."""
        nonlocal vision, vision_error
        try:
            from vision_filter import VisionFilter
            vision = VisionFilter()
            if vision.start():
                print(f"[VOICE] Vision filter loaded ({time.time() - load_start:.1f}s)")
            else:
                print("[VOICE] Vision filter: FAILED to start camera")
                vision = None
        except Exception as e:
            vision_error = e
            print(f"[VOICE] Vision filter: DISABLED - {e}")

    # Run both loaders in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(load_vosk), executor.submit(load_vision)]
        for f in as_completed(futures):
            pass  # Wait for all to complete

    print(f"[VOICE] Parallel load complete ({time.time() - load_start:.1f}s total)")

    # Check if Vosk loaded successfully
    if model is None:
        print("[VOICE] Vosk failed - falling back to text mode")
        return text_loop(demerzel)

    try:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        recognizer.SetMaxAlternatives(0)
        recognizer.SetWords(False)
    except Exception as e:
        print(f"[VOICE] KaldiRecognizer init failed: {e}")
        return text_loop(demerzel)

    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        print("[VOICE] Microphone stream opened")
    except Exception as e:
        print(f"[VOICE] Audio init failed: {e}")
        return text_loop(demerzel)

    # Vision status (already loaded in parallel above)

    print("-" * 60)
    print(f"Say '{WAKE_WORDS[0]}' to start...")

    # Helper to speak
    def speak(text: str, next_state: DemerzelState = DemerzelState.IDLE):
        """
        Speak with state management.

        CRITICAL: Microphone is PAUSED during speaking.
        This is STRUCTURAL selftalk prevention.

        Args:
            text: Text to speak
            next_state: State to transition to after speaking
        """
        if not text:
            return

        demerzel.transition(DemerzelState.SPEAKING, "TTS output")
        demerzel.record_spoken(text)

        # CRITICAL: Pause transcription during speaking
        stream.stop_stream()
        recognizer.Reset()

        if demerzel.tts:
            try:
                demerzel.tts.speak(text, stream, recognizer)
            except Exception as e:
                print(f"[VOICE] TTS error: {e}")
        else:
            print(f"[SPEAK] {text}")
            time.sleep(0.5)

        # Post-speech cleanup
        time.sleep(0.3)  # Audio buffer drain

        # Drain any audio that was captured during speech
        stream.start_stream()
        time.sleep(0.2)
        try:
            while stream.get_read_available() > 0:
                stream.read(CHUNK, exception_on_overflow=False)
        except:
            pass

        recognizer.Reset()
        demerzel.transition(next_state, "TTS complete")

    # Main loop
    while not shutdown_requested:
        try:
            # =================================================================
            # STATE: IDLE - Listen for wake word
            # =================================================================
            if demerzel.state == DemerzelState.IDLE:
                data = stream.read(CHUNK, exception_on_overflow=False)

                # Check for wake word in both final and partial results
                wake_detected = False

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()
                    for wake in WAKE_WORDS:
                        if wake in text:
                            # Vision gate: only block if face detected but lips not moving
                            if vision and vision.has_face() and not vision.is_human_speaking():
                                continue
                            print(f"[WAKE] Detected: '{text}'")
                            wake_detected = True
                            break
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get("partial", "").lower()
                    for wake in WAKE_WORDS:
                        if wake in partial_text:
                            # Vision gate: only block if face detected but lips not moving
                            if vision and vision.has_face() and not vision.is_human_speaking():
                                continue
                            print(f"[WAKE] Detected (partial): '{partial_text}'")
                            recognizer.Reset()
                            wake_detected = True
                            break

                if wake_detected:
                    # Say "Yes?" and then stay in LISTENING state to hear command
                    speak("Yes?", next_state=DemerzelState.LISTENING)
                    recognizer.Reset()

            # =================================================================
            # STATE: SLEEPING - Wait for wake word to wake up
            # =================================================================
            elif demerzel.state == DemerzelState.SLEEPING:
                data = stream.read(CHUNK, exception_on_overflow=False)

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()
                    for wake in WAKE_WORDS:
                        if wake in text:
                            print(f"[WAKE] Waking from sleep: '{text}'")
                            demerzel.wake()
                            speak("I'm awake. How can I help?", next_state=DemerzelState.LISTENING)
                            recognizer.Reset()
                            break

            # =================================================================
            # STATE: LISTENING - Transcribe command
            # =================================================================
            elif demerzel.state == DemerzelState.LISTENING:
                command = transcribe_command(recognizer, stream, timeout=12.0, vision=vision)

                if command:
                    # Check for echo
                    if demerzel.is_likely_echo(command):
                        print(f"[ECHO] Detected: '{command}' - ignoring")
                        demerzel.transition(DemerzelState.IDLE, "Echo detected")
                        continue

                    print(f"[COMMAND] {command}")
                    demerzel.transition(DemerzelState.PROCESSING, "Command received")

                    # Store in memory
                    if demerzel.memory:
                        try:
                            demerzel.memory.store_conversation("user", command)
                        except:
                            pass

                    # Process command
                    response = demerzel.process(command)

                    # Store response in memory
                    if demerzel.memory:
                        try:
                            demerzel.memory.store_conversation("demerzel", response)
                        except:
                            pass

                    # Speak response
                    speak(response)

                    # Check if we should sleep
                    if demerzel.state == DemerzelState.SLEEPING:
                        print("[VOICE] Going to sleep...")
                else:
                    # Timeout or silence
                    demerzel.transition(DemerzelState.IDLE, "Timeout")

            # =================================================================
            # STATE: PROCESSING - (Handled inline above)
            # =================================================================
            elif demerzel.state == DemerzelState.PROCESSING:
                # Processing happens inline in LISTENING state
                pass

            # =================================================================
            # STATE: SPEAKING - (Handled by speak() function)
            # =================================================================
            elif demerzel.state == DemerzelState.SPEAKING:
                # Speaking is blocking, handled by speak()
                pass

        except Exception as e:
            print(f"[VOICE] Error: {e}")
            demerzel.transition(DemerzelState.IDLE, f"Error: {e}")

    # Cleanup
    print("\n[VOICE] Shutting down...")
    if vision:
        try:
            vision.stop()
        except:
            pass
    stream.stop_stream()
    stream.close()
    p.terminate()
    if demerzel.memory:
        try:
            demerzel.memory.end_session()
        except:
            pass
    print("[VOICE] Session ended")


def transcribe_command(recognizer, stream, timeout: float = 12.0, vision=None) -> str:
    """
    Transcribe a command after wake word.
    Returns transcribed text or empty string on timeout.
    """
    CHUNK = 4096
    start_time = time.time()
    silence_start = None
    SILENCE_TIMEOUT = 2.0  # Stop after 2 seconds of silence
    last_partial = ""

    while (time.time() - start_time) < timeout:
        if shutdown_requested:
            return ""

        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except:
            return ""

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text
            else:
                # Empty final result - check for silence timeout
                if silence_start is None:
                    silence_start = time.time()
                elif (time.time() - silence_start) > SILENCE_TIMEOUT:
                    # Return last partial if we have one
                    if last_partial:
                        return last_partial
                    return ""
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text:
                last_partial = partial_text
                silence_start = None  # Reset silence timer

    # Timeout - return last partial if any
    return last_partial


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("DEMERZEL - R -> C -> I Architecture")
    print("=" * 60)
    print("R (Root Source): Alan - External ground truth")
    print("C (Constraints): This CODE - State machine, router, execution boundary")
    print("I (Intelligence): LLMs - Fungible tools called by C")
    print("-" * 60)

    # Parse mode argument
    mode = 'voice'
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('text', 'repl', 't'):
            mode = 'text'
        elif arg in ('voice', 'v'):
            mode = 'voice'
        elif arg in ('help', '-h', '--help'):
            print("\nUsage:")
            print("  python3 run_demerzel.py          # Voice mode (default)")
            print("  python3 run_demerzel.py voice    # Voice mode")
            print("  python3 run_demerzel.py text     # Text mode (REPL)")
            return 0

    # Initialize services
    print("\nInitializing services...")
    services = init_services()

    # Create Demerzel instance
    demerzel = get_demerzel(
        memory_manager=services.get('memory'),
        hardware_executor=services.get('hardware'),
        tts_service=services.get('tts'),
        transcription_service=services.get('transcriber'),
    )

    print(f"\nMode: {mode.upper()}")

    # Run appropriate loop
    if mode == 'text':
        text_loop(demerzel)
    else:
        voice_loop(demerzel)

    return 0


if __name__ == "__main__":
    sys.exit(main())
