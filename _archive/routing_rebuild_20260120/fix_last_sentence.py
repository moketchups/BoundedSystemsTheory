"""
Fix: Use last SENTENCE (sequence of words) and detect human speech during self-awareness.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find and replace the self-awareness listening section
old_awareness = '''    # Extract my last word for self-awareness
    words = text.lower().split()
    # Clean punctuation from last word
    last_word = words[-1].strip('.,!?;:\\'") if words else ""
    print(f"[SELF-AWARENESS] My last word is: \\'{last_word}\\'")'''

new_awareness = '''    # Extract last SENTENCE for self-awareness (more unique than single word)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    last_sentence = sentences[-1] if sentences else text
    # Get last 4 words as unique sequence
    last_words = [w.strip('.,!?;:\\'\"').lower() for w in last_sentence.split()][-4:]
    print(f"[SELF-AWARENESS] My last phrase is: \\'{' '.join(last_words)}\\'")'''

if old_awareness in content:
    content = content.replace(old_awareness, new_awareness)
    print("✅ Changed to last sentence detection")
else:
    print("❌ Pattern 1 not found")

# Fix the detection loop to check sequence and human speech
old_loop = '''        print(f"[SELF-AWARENESS] Listening for my last word \\'{last_word}\\'...")
        
        while time.time() - start_time < max_wait:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except:
                break
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                heard = result.get("text", "").strip().lower()
                
                if heard:
                    print(f"[SELF-AWARENESS] Heard: \\'{heard}\\'")
                    # Check if my last word is in what I heard
                    if last_word in heard.split():
                        print(f"[SELF-AWARENESS] Heard my last word \\'{last_word}\\' - I\\'m done speaking")
                        heard_last_word = True
                        break
            
            # Also check partial results for faster detection
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").lower()
            if last_word in partial_text.split():
                print(f"[SELF-AWARENESS] Heard last word in partial - I\\'m done speaking")
                heard_last_word = True
                break
        
        if not heard_last_word:
            print(f"[SELF-AWARENESS] Timeout waiting for last word, assuming done")'''

new_loop = '''        print(f"[SELF-AWARENESS] Listening for my last phrase...")
        heard_words_buffer = []
        
        while time.time() - start_time < max_wait:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except:
                break
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                heard = result.get("text", "").strip().lower()
                
                if heard:
                    heard_word_list = [w.strip('.,!?;:\\'\"') for w in heard.split()]
                    heard_words_buffer.extend(heard_word_list)
                    # Keep only last 20 words
                    heard_words_buffer = heard_words_buffer[-20:]
                    
                    # Check if last phrase appears IN SEQUENCE
                    buffer_str = ' '.join(heard_words_buffer)
                    phrase_str = ' '.join(last_words)
                    if phrase_str in buffer_str:
                        print(f"[SELF-AWARENESS] Heard my last phrase - I'm done speaking")
                        heard_last_word = True
                        break
                    
                    # Check if NON-SELF speech (human talking)
                    my_words = set(text.lower().split())
                    heard_set = set(heard_word_list)
                    non_self_ratio = len(heard_set - my_words) / max(len(heard_set), 1)
                    if non_self_ratio > 0.7 and len(heard_set) >= 3:
                        print(f"[SELF-AWARENESS] Detected non-self speech (human?), breaking out")
                        break
        
        if not heard_last_word:
            print(f"[SELF-AWARENESS] Done listening (timeout or human detected)")'''

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    print("✅ Fixed detection loop")
else:
    print("❌ Pattern 2 not found - checking variations...")

with open('brain_controller.py', 'w') as f:
    f.write(content)
