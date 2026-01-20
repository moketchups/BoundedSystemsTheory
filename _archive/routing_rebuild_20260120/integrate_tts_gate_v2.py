"""
Properly integrate TTSGate into brain_controller
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find and replace the speak function
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
    
    # Scale wait time based on response length
    # ~3 words/second at 175 wpm, plus base echo time'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, gate=None):
    """Speak text via TTS with echo suppression gating"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Start TTS gate - block audio processing
    if gate:
        gate.start_speaking()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Stop TTS gate - buffer period starts
    if gate:
        gate.stop_speaking()
    
    # Scale wait time based on response length
    # ~3 words/second at 175 wpm, plus base echo time'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Modified speak() to use TTSGate")
else:
    print("❌ Could not find speak function - checking variations...")
    # Show what we have
    import re
    match = re.search(r'def speak\([^)]+\):[^\n]*\n(?:[ \t]+[^\n]+\n){0,20}', content)
    if match:
        print("Found speak():")
        print(match.group(0)[:500])

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\nDone! Now checking all speak() calls...")
