with open('brain_controller.py', 'r') as f:
    content = f.read()

# Modify speak function to pause/resume stream
old = '''def speak(tts: pyttsx3.Engine, text: str):
    """Speak text via TTS"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    tts.say(text)
    tts.runAndWait()'''

new = '''def speak(tts: pyttsx3.Engine, text: str, stream=None):
    """Speak text via TTS"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Pause microphone to avoid hearing ourselves
    if stream:
        stream.stop_stream()
    
    tts.say(text)
    tts.runAndWait()
    
    # Resume microphone
    if stream:
        time.sleep(0.3)  # Brief pause after speech
        stream.start_stream()'''

content = content.replace(old, new)

# Update all speak() calls to pass stream
content = content.replace('speak(tts, "Yes?")', 'speak(tts, "Yes?", stream)')
content = content.replace('speak(tts, "I didn\'t hear anything.")', 'speak(tts, "I didn\'t hear anything.", stream)')
content = content.replace('speak(tts, cognitive_output.clarification_question)', 'speak(tts, cognitive_output.clarification_question, stream)')
content = content.replace('speak(tts, f"I cannot execute this code. {analysis.reasons[0]}")', 'speak(tts, f"I cannot execute this code. {analysis.reasons[0]}", stream)')
content = content.replace('speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.")', 'speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.", stream)')
content = content.replace('speak(tts, "Code execution cancelled.")', 'speak(tts, "Code execution cancelled.", stream)')
content = content.replace('speak(tts, "Are you sure? Say I\'m sure to proceed.")', 'speak(tts, "Are you sure? Say I\'m sure to proceed.", stream)')
content = content.replace('speak(tts, response)', 'speak(tts, response, stream)')
content = content.replace('speak(tts, router_output.speak)', 'speak(tts, router_output.speak, stream)')
content = content.replace('speak(tts, "Confirm sleep. Please say yes or no.")', 'speak(tts, "Confirm sleep. Please say yes or no.", stream)')
content = content.replace('speak(tts, "Going to sleep. Wake me when you need me.")', 'speak(tts, "Going to sleep. Wake me when you need me.", stream)')
content = content.replace('speak(tts, "Can you please complete your request?")', 'speak(tts, "Can you please complete your request?", stream)')
content = content.replace('speak(tts, "Action cancelled.")', 'speak(tts, "Action cancelled.", stream)')

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed microphone mute during TTS")
