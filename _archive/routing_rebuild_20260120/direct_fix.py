import re

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the self-awareness loop and add human detection
old_code = '''                if heard:
                    print(f"[SELF-AWARENESS] Heard: '{heard}'")
                    # Check if my last word is in what I heard
                    if last_word in heard.split():
                        print(f"[SELF-AWARENESS] Heard my last word '{last_word}' - I'm done speaking")
                        heard_last_word = True
                        break'''

new_code = '''                if heard:
                    print(f"[SELF-AWARENESS] Heard: '{heard}'")
                    
                    # Check if this is HUMAN speech (words NOT in my text)
                    my_words = set(w.strip('.,!?;:\\'\"').lower() for w in text.split())
                    heard_words = set(w.strip('.,!?;:\\'\"').lower() for w in heard.split())
                    non_self = heard_words - my_words
                    if len(non_self) >= 3 and len(heard_words) >= 4:
                        print(f"[SELF-AWARENESS] Human speaking! Non-self words: {non_self}")
                        # Store for follow-up processing
                        global pending_human_speech
                        pending_human_speech = heard
                        break
                    
                    # Check if my last word is in what I heard
                    if last_word in heard.split():
                        print(f"[SELF-AWARENESS] Heard my last word '{last_word}' - I'm done speaking")
                        heard_last_word = True
                        break'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Added human detection to self-awareness loop")
else:
    print("❌ Pattern not found")
    
# Add global variable
old_global = 'last_spoken_text = ""'
new_global = '''last_spoken_text = ""
pending_human_speech = ""  # Captured during self-awareness'''

if old_global in content:
    content = content.replace(old_global, new_global)
    print("✅ Added pending_human_speech global")

with open('brain_controller.py', 'w') as f:
    f.write(content)
