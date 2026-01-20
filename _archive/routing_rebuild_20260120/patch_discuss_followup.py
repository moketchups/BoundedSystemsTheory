"""Add follow-up mode to discuss handler"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

old = '''                print("[VOICE] Discussion complete, back to wake word mode")
                command = None
                continue'''

new = '''                # Follow-up mode after discuss
                print("[VOICE] Follow-up mode (3 seconds)...")
                follow_up_start = time.time()
                follow_up = ""
                
                while time.time() - follow_up_start < 3.0:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            follow_up = text
                            print(f"[FOLLOW-UP] Heard: '{text}'")
                            break
                
                if follow_up:
                    command = follow_up
                    print(f"[FOLLOW-UP] Processing: '{command}'")
                else:
                    print("[VOICE] No follow-up, back to wake word mode")
                    command = None
                continue'''

if old in content:
    content = content.replace(old, new)
    with open('brain_controller.py', 'w') as f:
        f.write(content)
    print("✅ Added follow-up to discuss handler")
else:
    print("❌ Pattern not found")
