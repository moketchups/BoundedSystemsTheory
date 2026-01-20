"""
Add tts_gate.should_process_audio() check before processing speech
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find where we process recognized text and add gate check
# Look for the pattern where we check if text was heard

# 1. Main recognition loop - after getting full command
old_full_cmd = '''            if result.get("text"):
                text = result["text"].strip().lower()
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0):.2f})")'''

new_full_cmd = '''            if result.get("text"):
                text = result["text"].strip().lower()
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0):.2f})")
                
                # Check TTS gate - ignore if Demerzel was just speaking
                if not tts_gate.should_process_audio():
                    print(f"[TTS GATE] Ignoring (Demerzel echo): '{text}'")
                    continue'''

if old_full_cmd in content:
    content = content.replace(old_full_cmd, new_full_cmd)
    print("✅ Added gate check after main recognition")
else:
    print("⚠️ Could not find main recognition pattern")

# 2. Follow-up recognition - similar pattern
old_followup = '''                if followup_result.get("text"):
                    followup_text = followup_result["text"].strip().lower()
                    print(f"[FOLLOW-UP] Got: '{followup_text}'"'''

new_followup = '''                if followup_result.get("text"):
                    followup_text = followup_result["text"].strip().lower()
                    
                    # Check TTS gate for follow-up
                    if not tts_gate.should_process_audio():
                        print(f"[TTS GATE] Ignoring follow-up (echo): '{followup_text}'")
                        continue
                    
                    print(f"[FOLLOW-UP] Got: '{followup_text}'"'''

if old_followup in content:
    content = content.replace(old_followup, new_followup)
    print("✅ Added gate check for follow-up recognition")
else:
    print("⚠️ Could not find follow-up pattern, searching...")
    # Try to find it
    import re
    match = re.search(r'\[FOLLOW-UP\] Got:', content)
    if match:
        print(f"   Found at position {match.start()}")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ TTS Gate integration complete!")
