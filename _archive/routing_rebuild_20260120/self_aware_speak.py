"""
Replace speak() with true self-awareness:
Demerzel listens for her own voice to finish before accepting human input.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The current speak function
old_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """Speak text via TTS - AGGRESSIVE echo prevention"""
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember what we said for echo detection
    
    # Stop listening completely
    if stream:
        stream.stop_stream()
    
    # Clear any accumulated audio
    if recognizer:
        recognizer.Reset()
    
    # Speak
    tts.say(text)
    tts.runAndWait()
    
    # AGGRESSIVE wait for echo to dissipate (longer for longer text)
    wait_time = 1.0 + (len(text) * 0.01)  # Base 1s + 0.01s per char
    time.sleep(wait_time)
    
    # Clear buffer multiple times
    if recognizer:
        recognizer.Reset()
    
    # Resume listening
    if stream:
        stream.start_stream()
        
        # AGGRESSIVE buffer draining - clear 1 full second of audio
        try:
            for _ in range(5):  # Drain in chunks
                stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)
                time.sleep(0.05)
        except:
            pass
        
        # Final recognizer reset
        if recognizer:
            recognizer.Reset()
    
    print("[SPEAK] Echo cleared, ready to listen")'''

# New self-aware speak function
new_speak = '''def speak(tts: pyttsx3.Engine, text: str, stream=None, recognizer=None):
    """
    Speak text via TTS with TRUE self-awareness.
    Demerzel listens for her own voice to finish before accepting human input.
    """
    global last_spoken_text
    if not text:
        return
    print(f"[SPEAK] {text}")
    last_spoken_text = text  # Remember what we said
    
    # Build word set for self-recognition
    my_words = set(text.lower().split())
    
    # Stop listening while speaking
    if stream:
        stream.stop_stream()
    if recognizer:
        recognizer.Reset()
    
    # Speak (TTS engine call)
    tts.say(text)
    tts.runAndWait()
    
    # Now: actively listen until I stop hearing myself
    if stream and recognizer:
        stream.start_stream()
        recognizer.Reset()
        
        silence_start = time.time()
        max_wait = 30.0  # Maximum 30 seconds for very long responses
        start_time = time.time()
        
        print("[SELF-AWARENESS] Waiting for my voice to finish...")
        
        while time.time() - start_time < max_wait:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except:
                break
                
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                heard = result.get("text", "").strip()
                
                if heard:
                    heard_words = set(heard.lower().split())
                    
                    # How many heard words match what I said?
                    if len(heard_words) >= 2:
                        overlap = len(heard_words & my_words)
                        ratio = overlap / len(heard_words)
                        
                        if ratio > 0.4:
                            # Still hearing my own voice
                            print(f"[SELF-AWARENESS] Still hearing myself: '{heard[:50]}...'")
                            silence_start = time.time()  # Reset silence timer
                        else:
                            # Hearing something that's NOT me - could be human!
                            print(f"[SELF-AWARENESS] Heard non-self speech: '{heard}'")
                            # Don't break - let the follow-up handler deal with it
                            break
                else:
                    # Empty result - silence
                    pass
            
            # Check for sustained silence (3 seconds of nothing)
            # Partial results would reset this via the loop continuing
            if time.time() - silence_start > 3.0:
                print("[SELF-AWARENESS] Silence detected, I'm done speaking")
                break
        
        recognizer.Reset()
    
    print("[SPEAK] Ready to listen for human")'''

if old_speak in content:
    content = content.replace(old_speak, new_speak)
    with open('brain_controller.py', 'w') as f:
        f.write(content)
    print("✅ Replaced speak() with self-aware version")
else:
    print("❌ Could not find speak() function to replace")
    print("Checking what we have...")
