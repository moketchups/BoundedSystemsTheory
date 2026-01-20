"""
Nuclear fix: Close mic stream during TTS, reopen fresh after
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the entire speak function
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, gate=None):
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
    
    # CRITICAL: Flush audio buffer to prevent echo
    # The mic was recording while TTS was playing - discard that audio
    if stream:
        try:
            # Read and discard any buffered audio
            while stream.get_read_available() > 0:
                stream.read(stream.get_read_available(), exception_on_overflow=False)
        except:
            pass'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, gate=None):
    """Speak text via TTS with echo suppression - stream stays stopped"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely - mic will stay off until explicitly restarted
    if stream:
        stream.stop_stream()
    
    # Start TTS gate
    if gate:
        gate.start_speaking()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Stop TTS gate
    if gate:
        gate.stop_speaking()
    
    # DO NOT restart stream here - let the caller handle it after echo dies'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Simplified speak() function")
else:
    print("❌ Could not find speak function")

# Now add stream restart logic before each follow-up mode
# Pattern: before "Follow-up mode (5 sec)..."
old_followup = '''                print("[VOICE] Follow-up mode (5 sec)...")'''

new_followup = '''                # Restart mic stream fresh after TTS echo dies
                if not stream.is_active():
                    time.sleep(1.5)  # Wait for echo to die
                    stream.start_stream()
                    # Flush any residual
                    try:
                        while stream.get_read_available() > 0:
                            stream.read(stream.get_read_available(), exception_on_overflow=False)
                    except:
                        pass
                print("[VOICE] Follow-up mode (5 sec)...")'''

count = content.count(old_followup)
if count > 0:
    content = content.replace(old_followup, new_followup)
    print(f"✅ Added stream restart before {count} follow-up modes")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ Nuclear echo fix applied")
