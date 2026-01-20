"""
Fix: use correct variable name 'command' not 'full_command'
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find current (broken) discuss handler
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                print("[VOICE] Discussion complete")
                full_command = ""  # Clear to prevent re-processing
                cognitive_output = None  # Clear output
                continue  # Back to main loop'''

# Fix: use correct variable name
new_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                print("[VOICE] Discussion complete, back to wake word mode")
                command = None  # CORRECT variable - clears so we wait for wake word
                continue'''

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Fixed variable name: command = None")
else:
    print("⚠️ Could not find exact pattern")

with open('brain_controller.py', 'w') as f:
    f.write(content)
