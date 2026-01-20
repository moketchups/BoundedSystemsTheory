with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find where recognizer is initialized and make it a function
old = '''    recognizer = init_vosk(VOSK_MODEL_PATH, SAMPLE_RATE)'''

new = '''    vosk_model = Model(VOSK_MODEL_PATH)
    
    def create_recognizer():
        """Create a fresh recognizer instance"""
        rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)
        rec.SetMaxAlternatives(0)
        rec.SetWords(False)
        return rec
    
    recognizer = create_recognizer()'''

content = content.replace(old, new)

# Add recognizer recreation after EVERY speak() call
# After wake word response
content = content.replace(
    '''            speak(tts, "Yes?", stream)
            
            # Get command''',
    '''            speak(tts, "Yes?", stream)
            recognizer = create_recognizer()  # Fresh recognizer after TTS
            
            # Get command'''
)

# After code execution
content = content.replace(
    '''                    speak(tts, response, stream)
                    # Store code execution in memory''',
    '''                    speak(tts, response, stream)
                    recognizer = create_recognizer()  # Fresh recognizer after TTS
                    # Store code execution in memory'''
)

content = content.replace(
    '''                    speak(tts, response, stream)
                    # Store code error in memory''',
    '''                    speak(tts, response, stream)
                    recognizer = create_recognizer()  # Fresh recognizer after TTS
                    # Store code error in memory'''
)

# After router responses
content = content.replace(
    '''                speak(tts, router_output.speak, stream)
                # Store demerzel response''',
    '''                speak(tts, router_output.speak, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                # Store demerzel response'''
)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("Step 2: Added recognizer recreation after all TTS")
