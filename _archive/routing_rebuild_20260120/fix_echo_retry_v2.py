"""
Add echo retry loop to the follow-up at line 312
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The exact current pattern (lines 312-340)
old_block = '''                print("[VOICE] Follow-up mode (5 sec)...")
                follow_up_start = time.time()
                follow_up = ""
                partial_detected = False
                
                while time.time() - follow_up_start < 5.0:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            follow_up = text
                            break
                    else:
                        partial = json.loads(recognizer.PartialResult())
                        partial_text = partial.get("partial", "").strip()
                        if partial_text and not partial_detected:
                            partial_detected = True
                
                if partial_detected and not follow_up:
                    final = json.loads(recognizer.FinalResult())
                    follow_up = final.get("text", "").strip()
                
                if follow_up:
                    command = follow_up
                    continue
                else:
                    command = None
                    continue'''

new_block = '''                # Follow-up with echo retry loop
                echo_retry = True
                while echo_retry:
                    echo_retry = False
                    print("[VOICE] Follow-up mode (5 sec)...")
                    follow_up_start = time.time()
                    follow_up = ""
                    partial_detected = False
                    
                    while time.time() - follow_up_start < 5.0:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            text = result.get("text", "").strip()
                            if text:
                                follow_up = text
                                break
                        else:
                            partial = json.loads(recognizer.PartialResult())
                            partial_text = partial.get("partial", "").strip()
                            if partial_text and not partial_detected:
                                partial_detected = True
                                print(f"[FOLLOW-UP] Hearing: '{partial_text}...'")
                    
                    if partial_detected and not follow_up:
                        final = json.loads(recognizer.FinalResult())
                        follow_up = final.get("text", "").strip()
                    
                    if follow_up:
                        # Demerzel thinks: "Is this my own voice?"
                        if is_likely_echo(follow_up, last_spoken_text):
                            print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                            recognizer = create_recognizer()
                            echo_retry = True  # Try again
                            continue
                        command = follow_up
                        continue
                    else:
                        command = None
                        continue'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ Added echo retry loop")
else:
    print("❌ Pattern not found - showing what we have:")
    # Debug
    import re
    match = re.search(r'Follow-up mode \(5 sec\)', content)
    if match:
        print(f"   Found at position {match.start()}")
        print(f"   Context: {content[match.start():match.start()+100]}")

with open('brain_controller.py', 'w') as f:
    f.write(content)
