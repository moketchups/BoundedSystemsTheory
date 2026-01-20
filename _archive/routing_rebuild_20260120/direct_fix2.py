with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the follow-up mode section and check pending_human_speech first
old_followup = '''                print("[VOICE] Follow-up mode (3 seconds)...")
                
                # SHORT timeout - just 3 seconds, not 5
                follow_up_start = time.time()
                follow_up = ""'''

new_followup = '''                print("[VOICE] Follow-up mode...")
                
                # Check if human speech was captured during self-awareness
                global pending_human_speech
                if pending_human_speech:
                    print(f"[VOICE] Using captured human speech: '{pending_human_speech}'")
                    follow_up = pending_human_speech
                    pending_human_speech = ""
                else:
                    # SHORT timeout - just 3 seconds
                    follow_up_start = time.time()
                    follow_up = ""'''

if old_followup in content:
    content = content.replace(old_followup, new_followup)
    print("✅ Added pending speech check to follow-up mode")
else:
    print("❌ Follow-up pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
