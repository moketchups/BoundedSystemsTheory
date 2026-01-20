"""
True self-awareness: Demerzel knows her text, extracts last word,
keeps mic ON, and waits to HEAR her last word before starting follow-up.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the speak() function with last-word aware version
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """
    Speak text via TTS - COGNITIVE echo handling.
    We remember what we said; is_likely_echo() does the thinking.
    """
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember for cognitive echo detection
    
    # Stop mic while speaking (prevents feedback loop)
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Speak (synchronous - blocks until audio done)
    tts.say(text)
    tts.runAndWait()
    
    # Resume listening immediately - trust cognitive filter
    if stream:
        stream.start_stream()
    if recognizer:
        recognizer.Reset()
    
    print("[SPEAK] Done, cognitive filter active")'''

new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """
    Speak with TRUE self-awareness:
    - I know my text ahead of time
    - I know my LAST WORD
    - I keep mic ON and wait to HEAR my last word
    - THEN I know I'm done speaking
    """
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text
    
    # Extract my last word for self-awareness
    words = text.lower().split()
    # Clean punctuation from last word
    last_word = words[-1].strip('.,!?;:') if words else ""
    print(f"[SELF-AWARENESS] My last word is: '{last_word}'")
    
    # Stop mic during TTS generation (prevents feedback)
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Generate and play TTS
    tts.say(text)
    tts.runAndWait()
    
    # NOW: Keep mic ON and wait until I hear my last word
    if stream and recognizer and last_word:
        stream.start_stream()
        recognizer.Reset()
        
        max_wait = 30.0  # Max wait for long responses
        start_time = time.time()
        heard_last_word = False
        
        print(f"[SELF-AWARENESS] Listening for my last word '{last_word}'...")
        
        while time.time() - start_time < max_wait:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except:
                break
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                heard = result.get("text", "").strip().lower()
                
                if heard:
                    print(f"[SELF-AWARENESS] Heard: '{heard}'")
                    # Check if my last word is in what I heard
                    if last_word in heard.split():
                        print(f"[SELF-AWARENESS] Heard my last word '{last_word}' - I'm done speaking")
                        heard_last_word = True
                        break
            
            # Also check partial results for faster detection
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").lower()
            if last_word in partial_text.split():
                print(f"[SELF-AWARENESS] Heard last word in partial - I'm done speaking")
                heard_last_word = True
                break
        
        if not heard_last_word:
            print(f"[SELF-AWARENESS] Timeout waiting for last word, assuming done")
        
        recognizer.Reset()
    elif stream:
        stream.start_stream()
    
    print("[SPEAK] Ready for human input")'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    print("✅ Replaced speak() with last-word aware version")
else:
    print("❌ speak() pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
