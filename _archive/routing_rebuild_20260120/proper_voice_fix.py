with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace speak function with proper implementation
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None):
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

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - properly mute mic and clear buffer"""
    if not text:
        return
    print(f"[SPEAK] {text}")
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Clear any accumulated audio
    if recognizer:
        recognizer.Reset()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # Wait for echo to dissipate
    time.sleep(0.5)
    
    # Clear buffer again
    if recognizer:
        recognizer.Reset()
    
    # Resume listening
    if stream:
        stream.start_stream()
        # Drain initial buffer (first 0.2 seconds might have echo)
        stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)'''

content = content.replace(old_speak, new_speak)

# Update ALL speak calls to pass recognizer
content = content.replace(
    'speak(tts, "Yes?", stream)',
    'speak(tts, "Yes?", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "I didn\'t hear anything.", stream)',
    'speak(tts, "I didn\'t hear anything.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, cognitive_output.clarification_question, stream)',
    'speak(tts, cognitive_output.clarification_question, stream, recognizer)'
)
content = content.replace(
    'speak(tts, f"I cannot execute this code. {analysis.reasons[0]}", stream)',
    'speak(tts, f"I cannot execute this code. {analysis.reasons[0]}", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.", stream)',
    'speak(tts, "This code has high risk patterns. Say yes to proceed or no to cancel.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Code execution cancelled.", stream)',
    'speak(tts, "Code execution cancelled.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Are you sure? Say I\'m sure to proceed.", stream)',
    'speak(tts, "Are you sure? Say I\'m sure to proceed.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, response, stream)',
    'speak(tts, response, stream, recognizer)'
)
content = content.replace(
    'speak(tts, router_output.speak, stream)',
    'speak(tts, router_output.speak, stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Confirm sleep. Please say yes or no.", stream)',
    'speak(tts, "Confirm sleep. Please say yes or no.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Going to sleep. Wake me when you need me.", stream)',
    'speak(tts, "Going to sleep. Wake me when you need me.", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Can you please complete your request?", stream)',
    'speak(tts, "Can you please complete your request?", stream, recognizer)'
)
content = content.replace(
    'speak(tts, "Action cancelled.", stream)',
    'speak(tts, "Action cancelled.", stream, recognizer)'
)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("Step 1: Fixed speak function with proper buffer clearing")
