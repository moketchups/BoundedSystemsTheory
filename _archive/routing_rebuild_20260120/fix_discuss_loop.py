"""
Fix the loop bug - return to wake word mode after discuss
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find our discuss handler and fix it to break out of follow-up mode
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                continue'''

new_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                break  # Return to wake word mode after discuss'''

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Fixed discuss loop - now returns to wake word mode")
else:
    print("⚠️ Could not find discuss handler")

with open('brain_controller.py', 'w') as f:
    f.write(content)
