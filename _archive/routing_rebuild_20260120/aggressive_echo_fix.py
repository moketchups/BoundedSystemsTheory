with open('brain_controller.py', 'r') as f:
    content = f.read()

# Make the buffer clearing MUCH more aggressive
old = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - properly mute mic and clear buffer"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Clear any accumulated audio
    if recognizer:
        recognizer.Reset()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Wait for echo to dissipate
    time.sleep(0.5)
    
    # Clear buffer again
    if recognizer:
        recognizer.Reset()
    
    # Resume listening
    if stream:
        stream.start_stream()
        # Drain initial buffer (first 0.2 seconds might have echo)
        stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)'''

new = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - AGGRESSIVE echo prevention"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
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

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Applied AGGRESSIVE echo prevention")
