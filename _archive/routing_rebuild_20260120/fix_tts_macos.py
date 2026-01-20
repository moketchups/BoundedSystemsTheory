"""
Replace pyttsx3 with macOS native 'say' command
"""
with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find and replace the speak function to use 'say' command
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
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

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """
    Speak text via macOS 'say' command (more reliable than pyttsx3)
    """
    global last_spoken_text
    import subprocess
    
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text
    
    # Stop mic while speaking
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Use macOS native 'say' command - much more reliable
    try:
        subprocess.run(['say', '-r', '175', text], check=True)
    except Exception as e:
        print(f"[SPEAK ERROR] {e}")
    
    # Resume listening
    if stream:
        stream.start_stream()
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done, cognitive filter active")'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Replaced pyttsx3 with macOS 'say' command")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
