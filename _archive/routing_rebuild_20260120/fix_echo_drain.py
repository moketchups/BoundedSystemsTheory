with open('brain_controller.py', 'r') as f:
    content = f.read()

old_code = '''    # Resume listening
    if stream:
        stream.start_stream()
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done")'''

new_code = '''    # Resume listening
    if stream:
        stream.start_stream()
        # Drain residual audio buffer (prevents hearing ourselves)
        time.sleep(0.3)
        try:
            while stream.get_read_available() > 0:
                stream.read(4096, exception_on_overflow=False)
        except:
            pass
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done")'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('brain_controller.py', 'w') as f:
        f.write(content)
    print("✅ Added buffer drain after speaking")
else:
    print("❌ Pattern not found")
    print("Looking for this exact text:")
    print(repr(old_code))
