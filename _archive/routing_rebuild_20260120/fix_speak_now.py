"""
Direct replacement - find speak function and use subprocess say
"""
import re

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the speak function using regex and replace it entirely
pattern = r'def speak\(tts: pyttsx3\.Engine, text: str, stream=None, recognizer=None\):.*?(?=\ndef [a-z])'

replacement = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text - using pyttsx3 with explicit voice"""
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text
    
    # Stop mic while speaking
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Use pyttsx3 with Samantha voice (clear female voice)
    try:
        tts.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
        tts.setProperty('rate', 175)
        tts.say(text)
        tts.runAndWait()
    except Exception as e:
        print(f"[SPEAK ERROR] {e}")
    
    # Resume listening
    if stream:
        stream.start_stream()
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done")

'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content != content:
    with open('brain_controller.py', 'w') as f:
        f.write(new_content)
    print("✅ Replaced speak function")
else:
    print("❌ Pattern not found, trying line-based approach...")
    
    # Fallback: Find and show current speak function
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('def speak('):
            print(f"Found speak at line {i+1}")
            print('\n'.join(lines[i:i+20]))
            break
