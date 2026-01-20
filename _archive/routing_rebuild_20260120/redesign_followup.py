with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the automatic follow-up with beep-activated follow-up
old = '''                # Stay awake - listen for follow-up WITHOUT wake word detection
                print("[VOICE] Ready for follow-up (no wake word needed)...")
                time.sleep(0.3)  # Brief pause
                
                # Get follow-up directly (no wake word check)
                follow_up = transcribe_command(recognizer, stream, timeout=5.0)
                if follow_up:
                    command = follow_up
                    print(f"[FOLLOW-UP] Processing: '{command}'")
                    # Loop back to process this command
                continue'''

new = '''                # Quick beep to signal "ready for follow-up"
                # User can either speak immediately OR ignore and we go back to wake word mode
                print("[VOICE] Follow-up mode (3 seconds)...")
                
                # SHORT timeout - just 3 seconds, not 5
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
                    # Loop back to process this command
                else:
                    print("[VOICE] No follow-up detected, back to wake word mode")
                continue'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Redesigned follow-up mode (3 second window, back to wake if silent)")
