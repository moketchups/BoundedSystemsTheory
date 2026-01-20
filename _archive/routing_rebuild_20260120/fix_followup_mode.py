"""
Fix: Add follow-up mode after discuss and router responses
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the discuss handler to use follow-up mode
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                print("[VOICE] Discussion complete, back to wake word mode")
                command = None  # CORRECT variable - clears so we wait for wake word
                continue'''

new_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                
                # Follow-up mode after discuss
                time.sleep(0.5)
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
                            print(f"[FOLLOW-UP] Got: '{text}'")
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
                    print(f"[FOLLOW-UP] Processing: '{command}'")
                    continue
                else:
                    print("[VOICE] No follow-up, back to wake mode")
                    command = None
                    continue'''

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Added follow-up mode after discuss")
else:
    print("⚠️ Could not find discuss handler")

# Now add follow-up after router response (before clearing command)
old_router_end = '''            # Clear command for next iteration
            command = None'''

new_router_end = '''            # Follow-up mode after router response (for confirmations, etc.)
            recognizer = create_recognizer()
            time.sleep(0.5)
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
                        print(f"[FOLLOW-UP] Got: '{text}'")
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
                print(f"[FOLLOW-UP] Processing: '{command}'")
                continue
            
            # No follow-up, clear command for next iteration
            command = None'''

if old_router_end in content:
    content = content.replace(old_router_end, new_router_end)
    print("✅ Added follow-up mode after router response")
else:
    print("⚠️ Could not find router end section")

with open('brain_controller.py', 'w') as f:
    f.write(content)
