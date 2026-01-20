with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the main loop and add command check
old = '''    try:
        while True:
            # Wait for wake word
            if not listen_for_wake_word(recognizer, stream, wake_words):
                continue
            
            speak(tts, "Yes?", stream)
            recognizer = create_recognizer()  # Fresh recognizer after TTS
            
            # Get command with longer timeout
            command = transcribe_command(recognizer, stream, timeout=8.0)'''

new = '''    try:
        command = None  # Initialize command variable
        while True:
            # If we don't already have a command (from follow-up), wait for wake word
            if not command:
                if not listen_for_wake_word(recognizer, stream, wake_words):
                    continue
                
                speak(tts, "Yes?", stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                
                # Get command with longer timeout
                command = transcribe_command(recognizer, stream, timeout=8.0)'''

content = content.replace(old, new)

# At the end of processing, clear command before looping
old = '''            # Handle sleep mode
            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()
                memory.clear_working_memory()
                speak(tts, "Going to sleep. Wake me when you need me.", stream)'''

new = '''            # Handle sleep mode
            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()
                memory.clear_working_memory()
                speak(tts, "Going to sleep. Wake me when you need me.", stream)
            
            # Clear command for next iteration
            command = None'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed follow-up loop flow")
