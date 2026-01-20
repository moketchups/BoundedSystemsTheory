"""
Give Demerzel the ability to recognize her own echo through critical thought.
She knows what she just said. She can figure it out.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Track last spoken text globally
# Add after imports
import_marker = 'from tts_gate import TTSGate'
new_import = '''from tts_gate import TTSGate

# Track what Demerzel last said (for echo detection)
last_spoken_text = ""'''

content = content.replace(import_marker, new_import)
print("✅ Added last_spoken_text tracker")

# Update speak() to remember what was said
old_speak_start = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, gate=None):
    """Speak text via TTS with echo suppression - stream stays stopped"""
    if not text:
        return
    print(f"[SPEAK] {text}")'''

new_speak_start = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, gate=None):
    """Speak text via TTS with echo suppression - stream stays stopped"""
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember what we said'''

if old_speak_start in content:
    content = content.replace(old_speak_start, new_speak_start)
    print("✅ speak() now remembers what was said")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ Step 1 complete: Demerzel now remembers what she said")
