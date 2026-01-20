"""
Fix: When awaiting confirmation, bypass cognitive and send directly to router
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find where we process through cognitive layer and add confirmation check
old_cognitive = '''            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Store user input in memory
            memory.store_conversation("user", command)
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)'''

new_cognitive = '''            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Store user input in memory
            memory.store_conversation("user", command)
            
            # Check if router is awaiting confirmation - bypass cognitive layer
            if router.is_awaiting_confirmation():
                print("[CONFIRM] Router awaiting confirmation, bypassing cognitive")
                router_output = router.route_text(command)
                print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")
                
                if router_output.speak:
                    speak(tts, router_output.speak, stream)
                    recognizer = create_recognizer()
                    memory.store_conversation("demerzel", router_output.speak,
                                            intent=str(router_output.intent),
                                            executed=router_output.did_execute)
                
                # Stay in follow-up mode for potential second confirmation
                time.sleep(1.5)
                for _ in range(15):
                    try:
                        stream.read(int(SAMPLE_RATE * 0.15), exception_on_overflow=False)
                    except:
                        pass
                recognizer = create_recognizer()
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
                
                if partial_detected and not follow_up:
                    final = json.loads(recognizer.FinalResult())
                    follow_up = final.get("text", "").strip()
                
                if follow_up:
                    command = follow_up
                    continue
                else:
                    command = None
                    continue
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)'''

if old_cognitive in content:
    content = content.replace(old_cognitive, new_cognitive)
    print("✅ Added confirmation bypass logic")
else:
    print("⚠️ Could not find cognitive processing section")

with open('brain_controller.py', 'w') as f:
    f.write(content)
