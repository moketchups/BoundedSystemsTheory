"""
Fix tts_gate scope - pass it to transcribe_command function
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

changes = 0

# 1. Update transcribe_command function signature to accept tts_gate
old_func = 'def transcribe_command(recognizer, stream, timeout: float = 5.0):'
new_func = 'def transcribe_command(recognizer, stream, tts_gate, timeout: float = 5.0):'

if old_func in content:
    content = content.replace(old_func, new_func)
    changes += 1
    print("✅ Updated transcribe_command signature")
else:
    print("❌ Could not find transcribe_command signature")

# 2. Update all calls to transcribe_command to pass tts_gate
# Pattern: transcribe_command(recognizer, stream, timeout=X)
import re

# Find all calls and add tts_gate parameter
old_call = r'transcribe_command\(recognizer, stream,'
new_call = 'transcribe_command(recognizer, stream, tts_gate,'

content, count = re.subn(old_call, new_call, content)
if count > 0:
    changes += count
    print(f"✅ Updated {count} calls to transcribe_command")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print(f"\n✅ Made {changes} changes")
