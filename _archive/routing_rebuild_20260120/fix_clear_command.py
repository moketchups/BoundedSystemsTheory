"""
Clear full_command after discuss to prevent re-processing
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find current discuss handler
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                print("[VOICE] Discussion complete, returning to wake word mode")
                continue  # Back to wake word detection (not break!)'''

# Fix: Clear the command AND set a flag to return to wake word mode
new_discuss = '''            # Handle discuss command - speak the discussion directly
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

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Fixed discuss handler - now clears full_command")
else:
    print("⚠️ Could not find exact discuss handler")

with open('brain_controller.py', 'w') as f:
    f.write(content)
