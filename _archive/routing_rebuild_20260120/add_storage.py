with open('brain_controller.py', 'r') as f:
    content = f.read()

# Add storage after user input is captured
old_code = '''            # Process with cognitive layer
            cognitive_output = cognitive.process(full_command)'''

new_code = '''            # Store user input in memory
            memory.store_conversation("user", full_command)
            
            # Process with cognitive layer
            cognitive_output = cognitive.process(full_command)'''

content = content.replace(old_code, new_code)

# Add storage after demerzel responds
old_code = '''            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak)'''

new_code = '''            # Handle response
            if router_output.speak:
                speak(tts, router_output.speak)
                # Store demerzel response
                memory.store_conversation("demerzel", router_output.speak, 
                                        intent=str(router_output.intent),
                                        executed=router_output.did_execute)'''

content = content.replace(old_code, new_code)

# Add memory clearing on sleep
old_code = '''            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()'''

new_code = '''            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()
                memory.clear_working_memory()'''

content = content.replace(old_code, new_code)

# Add session end on exit
old_code = '''    finally:
        print("[VOICE] Shutting down...")'''

new_code = '''    finally:
        print("[VOICE] Shutting down...")
        memory.end_session()'''

content = content.replace(old_code, new_code)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("Step 2: Added conversation storage hooks")
