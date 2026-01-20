"""Update speak() to track last spoken text"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - AGGRESSIVE echo prevention"""
    if not text:
        return
    print(f"[SPEAK] {text}")'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - AGGRESSIVE echo prevention"""
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember what we said for echo detection'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ speak() now tracks last_spoken_text")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
