"""
Wrap follow-up in retry loop so after echo detection we try again
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Pattern: The follow-up block at line 312
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
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                        command = ""
                        follow_up = ""
                        # Reset and keep listening for real input
                        recognizer = create_recognizer()
                        follow_up_start = time.time()  # Reset timer
                        continue  # Stay in follow-up loop'''

new_block = '''                # Follow-up with echo retry
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
                        command = follow_up
                        # Demerzel thinks: "Is this my own voice?"
                        if is_likely_echo(command, last_spoken_text):
                            print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                            recognizer = create_recognizer()
                            echo_retry = True  # Try again
                            continue'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ Added echo retry loop (location 1)")
else:
    print("❌ Could not find pattern 1")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ Echo retry loop added")
