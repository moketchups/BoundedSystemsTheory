"""
Add proper buffer flushing after TTS - the REAL fix
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the speak function and add buffer flushing
old_speak = '''    # Stop TTS gate - buffer period starts
    if gate:
        gate.stop_speaking()'''

new_speak = '''    # Stop TTS gate - buffer period starts
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

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Added audio buffer flush after TTS")
else:
    print("❌ Could not find TTS gate stop pattern")
    # Show what we have
    import re
    match = re.search(r'gate\.stop_speaking\(\)', content)
    if match:
        print(f"   Found stop_speaking at position {match.start()}")

with open('brain_controller.py', 'w') as f:
    f.write(content)
