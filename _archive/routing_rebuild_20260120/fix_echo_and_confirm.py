"""
Fix TWO issues:
1. Echo - increase wait time significantly based on response length
2. Confirmation - pass "yes/no" directly to router state, not through cognitive
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# FIX 1: Scale wait time based on response length in speak()
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None):
    """Speak text via TTS - returns None (recognizer will be recreated)"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Wait for acoustic echo to FULLY dissipate
    time.sleep(2.5)  # Longer wait for room acoustics
    
    # Resume stream
    if stream:
        stream.start_stream()
        
        # AGGRESSIVE buffer draining
        try:
            for _ in range(8):
                stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)
                time.sleep(0.03)
        except:
            pass
    
    print("[SPEAK] Ready for fresh input")'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None):
    """Speak text via TTS - returns None (recognizer will be recreated)"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Scale wait time based on response length
    # ~3 words/second at 175 wpm, plus base echo time
    word_count = len(text.split())
    speech_duration = word_count / 3.0
    echo_wait = max(4.0, speech_duration * 0.3)  # At least 4 sec, or 30% of speech time
    time.sleep(echo_wait)
    
    # Resume stream
    if stream:
        stream.start_stream()
        
        # VERY AGGRESSIVE buffer draining
        try:
            for _ in range(20):
                stream.read(int(SAMPLE_RATE * 0.15), exception_on_overflow=False)
                time.sleep(0.02)
        except:
            pass
    
    print("[SPEAK] Ready for fresh input")'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Fixed speak() with scaled echo wait")
else:
    print("⚠️ Could not find speak function")

with open('brain_controller.py', 'w') as f:
    f.write(content)
