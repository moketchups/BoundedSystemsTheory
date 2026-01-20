"""
Fix discuss - don't exit program, just go back to wake word mode
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the current handler with break
old_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                full_command = ""  # Clear to prevent re-processing
                break  # Return to wake word mode'''

# Fix: use continue instead of break, and properly reset state
new_discuss = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                print("[VOICE] Discussion complete, returning to wake word mode")
                continue  # Back to wake word detection (not break!)'''

if old_discuss in content:
    content = content.replace(old_discuss, new_discuss)
    print("✅ Fixed discuss handler - now uses continue instead of break")
else:
    print("⚠️ Could not find discuss handler")
    # Try to find alternative patterns
    if 'break  # Return to wake word mode' in content:
        content = content.replace('break  # Return to wake word mode', 
                                  'print("[VOICE] Back to wake word mode")\n                continue')
        print("✅ Fixed break -> continue (alt method)")

with open('brain_controller.py', 'w') as f:
    f.write(content)
