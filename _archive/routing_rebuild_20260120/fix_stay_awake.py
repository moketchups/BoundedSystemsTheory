with open('brain_controller.py', 'r') as f:
    content = f.read()

# Add stay-awake mode after successful command
old = '''            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak)
                # Store demerzel response
                memory.store_conversation("demerzel", router_output.speak, 
                                        intent=str(router_output.intent),
                                        executed=router_output.did_execute)
            
            # Handle sleep mode
            if router_output.sleep_mode:'''

new = '''            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak)
                # Store demerzel response
                memory.store_conversation("demerzel", router_output.speak, 
                                        intent=str(router_output.intent),
                                        executed=router_output.did_execute)
            
            # Stay awake for follow-up (no wake word needed for 30 seconds)
            if not router_output.sleep_mode and not router_output.needs_confirm:
                print("[VOICE] Staying awake for follow-up...")
                time.sleep(1)  # Brief pause
                
                # Listen for immediate follow-up (no wake word needed)
                follow_up = transcribe_command(recognizer, stream, timeout=5.0)
                if follow_up:
                    # Process follow-up without wake word
                    continue
            
            # Handle sleep mode
            if router_output.sleep_mode:'''

content = content.replace(old, new)

# Fix confirmation to not detect wake words
old = '''                # HIGH_RISK code - requires confirmation
                if analysis.risk_level == RiskLevel.HIGH:
                    speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.")
                    
                    confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "yes" not in confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        continue
                    
                    speak(tts, "Are you sure? Say I'm sure to proceed.")
                    final_confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "sure" not in final_confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        continue'''

new = '''                # HIGH_RISK code - requires confirmation
                if analysis.risk_level == RiskLevel.HIGH:
                    speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.")
                    
                    # Dedicated confirmation mode (no wake word detection)
                    print("[CONFIRMATION] Waiting for yes/no...")
                    confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "yes" not in confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        memory.store_conversation("demerzel", "Code execution cancelled.", 
                                                intent="CODE_CANCELLED", executed=False)
                        continue
                    
                    speak(tts, "Are you sure? Say I'm sure to proceed.")
                    print("[CONFIRMATION] Waiting for confirmation...")
                    final_confirm = transcribe_command(recognizer, stream, timeout=5.0)
                    if "sure" not in final_confirm.lower():
                        speak(tts, "Code execution cancelled.")
                        memory.store_conversation("demerzel", "Code execution cancelled.",
                                                intent="CODE_CANCELLED", executed=False)
                        continue'''

content = content.replace(old, new)

# Add same fix for router confirmation (LED, sleep, etc)
old = '''            # Route command through kernel
            router_output = router.route_text(cognitive_output.router_command)
            
            print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")'''

new = '''            # Route command through kernel
            router_output = router.route_text(cognitive_output.router_command)
            
            print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")
            
            # Handle confirmation requests from router
            if router_output.needs_confirm:
                print("[CONFIRMATION] HIGH_RISK action - waiting for yes/no...")
                confirm = transcribe_command(recognizer, stream, timeout=5.0)
                
                if "yes" in confirm.lower():
                    # Re-route with confirmation
                    router_output = router.route_text(cognitive_output.router_command + " CONFIRMED")
                    print(f"[RESULT] Confirmed: intent={router_output.intent}, executed={router_output.did_execute}")
                else:
                    speak(tts, "Action cancelled.")
                    memory.store_conversation("demerzel", "Action cancelled.",
                                            intent="CANCELLED", executed=False)
                    continue'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed stay-awake mode and confirmation handling")
