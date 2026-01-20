"""
Fix discuss to stay in conversation but not re-process same command
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the current (broken) discuss handler with break
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                break  # Return to wake word mode after discuss'''

# Fix: return to wake word mode properly by breaking out of inner loop only
new_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                full_command = ""  # Clear to prevent re-processing
                break  # Return to wake word mode'''

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Updated discuss handler")
else:
    print("⚠️ Could not find discuss handler - checking alternatives")

with open('brain_controller.py', 'w') as f:
    f.write(content)
