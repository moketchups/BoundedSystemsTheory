"""
Increase TTS gate buffer to handle room reverb
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Increase buffer from 0.8s to 2.5s
old = 'tts_gate = TTSGate(post_speech_buffer=0.8)'
new = 'tts_gate = TTSGate(post_speech_buffer=2.5)'

if old in content:
    content = content.replace(old, new)
    print("✅ Increased buffer to 2.5 seconds")
else:
    print("❌ Could not find buffer setting")

# Also update the print message
old_msg = '[TTS GATE] Initialized (0.8s buffer)'
new_msg = '[TTS GATE] Initialized (2.5s buffer)'
content = content.replace(old_msg, new_msg)

with open('brain_controller.py', 'w') as f:
    f.write(content)
