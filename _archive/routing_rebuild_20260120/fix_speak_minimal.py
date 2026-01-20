"""
Replace speak() with minimal version.
Trust is_likely_echo() to do the thinking, not hardcoded delays.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - AGGRESSIVE echo prevention"""
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember what we said for echo detection
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Clear any accumulated audio
    if recognizer:
        recognizer.Reset()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # AGGRESSIVE wait for echo to dissipate (longer for longer text)
    wait_time = 1.0 + (len(text) * 0.01)  # Base 1s + 0.01s per char
    time.sleep(wait_time)
    
    # Clear buffer multiple times
    if recognizer:
        recognizer.Reset()
    
    # Resume listening
    if stream:
        stream.start_stream()
        
        # AGGRESSIVE buffer draining - clear 1 full second of audio
        try:
            for _ in range(5):  # Drain in chunks
                stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)
                time.sleep(0.05)
        except:
            pass
        
        # Final recognizer reset
        if recognizer:
            recognizer.Reset()
    
    print("[SPEAK] Echo cleared, ready to listen")'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
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
    
    print("[SPEAK] Done, cognitive filter active")'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    with open('brain_controller.py', 'w') as f:
        f.write(content)
    print("✅ Replaced speak() with minimal cognitive version")
else:
    print("❌ Pattern not found")
