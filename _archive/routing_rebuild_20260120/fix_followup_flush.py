"""
Add aggressive buffer flush before EACH follow-up mode
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

changes = 0

# Pattern 1: Line 276 area - after "Ready for fresh input"
old1 = '''                recognizer = create_recognizer()
                print("[VOICE] Follow-up mode (5 sec)...")'''

new1 = '''                # Aggressive flush: clear ALL buffered audio from TTS playback
                try:
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                    time.sleep(0.3)  # Let any remaining echo die
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                except:
                    pass
                recognizer = create_recognizer()
                print("[VOICE] Follow-up mode (5 sec)...")'''

if old1 in content:
    content = content.replace(old1, new1)
    changes += 1
    print("✅ Added aggressive flush before follow-up mode (location 1)")

# Pattern 2: Line 384 area
old2 = '''                # Follow-up mode with fresh recognizer
                recognizer = create_recognizer()'''

new2 = '''                # Follow-up mode with fresh recognizer
                # Aggressive flush first
                try:
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                    time.sleep(0.3)
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                except:
                    pass
                recognizer = create_recognizer()'''

if old2 in content:
    content = content.replace(old2, new2)
    changes += 1
    print("✅ Added aggressive flush before follow-up mode (location 2)")

# Pattern 3: Line 444 area
old3 = '''                # Follow-up mode after discuss
                recognizer = create_recognizer()'''

new3 = '''                # Follow-up mode after discuss
                # Aggressive flush first
                try:
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                    time.sleep(0.3)
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                except:
                    pass
                recognizer = create_recognizer()'''

if old3 in content:
    content = content.replace(old3, new3)
    changes += 1
    print("✅ Added aggressive flush before follow-up mode (location 3)")

# Pattern 4: Line 511 area  
old4 = '''            # Follow-up mode after router response (for confirmations, etc.)
            recognizer = create_recognizer()'''

new4 = '''            # Follow-up mode after router response (for confirmations, etc.)
            # Aggressive flush first
            try:
                while stream.get_read_available() > 0:
                    stream.read(stream.get_read_available(), exception_on_overflow=False)
                time.sleep(0.3)
                while stream.get_read_available() > 0:
                    stream.read(stream.get_read_available(), exception_on_overflow=False)
            except:
                pass
            recognizer = create_recognizer()'''

if old4 in content:
    content = content.replace(old4, new4)
    changes += 1
    print("✅ Added aggressive flush before follow-up mode (location 4)")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print(f"\n✅ Added {changes} aggressive flushes")
