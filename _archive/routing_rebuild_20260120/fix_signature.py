"""
Fix transcribe_command signature
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

old_sig = 'def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 8.0) -> str:'
new_sig = 'def transcribe_command(recognizer: KaldiRecognizer, stream, tts_gate, timeout: float = 8.0) -> str:'

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("✅ Fixed transcribe_command signature")
else:
    print("❌ Could not find signature")

with open('brain_controller.py', 'w') as f:
    f.write(content)
