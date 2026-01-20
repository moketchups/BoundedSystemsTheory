with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the follow-up detection logic
old = '''                # Quick beep to signal "ready for follow-up"
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
                    print("[VOICE] No follow-up detected, back to wake word mode")'''

new = '''                # Follow-up mode - listen for continuation
                print("[VOICE] Follow-up mode (5 seconds, speak now)...")
                
                # Longer timeout, check BOTH partial and final results
                follow_up_start = time.time()
                follow_up = ""
                partial_detected = False
                
                while time.time() - follow_up_start < 5.0:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    
                    # Check for complete utterance
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            follow_up = text
                            print(f"[FOLLOW-UP] Complete: '{text}'")
                            break
                    else:
                        # Check partial results to detect speech
                        partial_result = json.loads(recognizer.PartialResult())
                        partial_text = partial_result.get("partial", "").strip()
                        if partial_text and not partial_detected:
                            partial_detected = True
                            print(f"[FOLLOW-UP] Detecting speech: '{partial_text}...'")
                
                # If we detected partial speech but didn't get complete utterance, get final result
                if partial_detected and not follow_up:
                    final_result = json.loads(recognizer.FinalResult())
                    follow_up = final_result.get("text", "").strip()
                    if follow_up:
                        print(f"[FOLLOW-UP] Final: '{follow_up}'")
                
                if follow_up:
                    command = follow_up
                    print(f"[FOLLOW-UP] Processing: '{command}'")
                    # Loop back to process this command
                else:
                    print("[VOICE] No follow-up, back to wake word mode")'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed follow-up detection (5 sec window + partial result detection)")
