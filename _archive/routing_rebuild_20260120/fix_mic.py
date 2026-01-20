"""
Set Yeti Nano as mic
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The pattern uses 'rate' variable
old_stream = '''stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk)'''

new_stream = '''stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            input_device_index=1,  # Yeti Nano
            frames_per_buffer=chunk)'''

if old_stream in content:
    content = content.replace(old_stream, new_stream)
    print("✅ Set Yeti Nano as input device")
else:
    print("❌ Pattern not found, trying regex...")
    import re
    # More flexible pattern
    pattern = r'(stream = p\.open\([^)]*input=True,)\s*(\n\s*frames_per_buffer)'
    replacement = r'\1\n            input_device_index=1,  # Yeti Nano\2'
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        content = new_content
        print(f"✅ Set Yeti Nano via regex ({count} replacements)")
    else:
        print("❌ Could not find stream pattern")

with open('brain_controller.py', 'w') as f:
    f.write(content)
