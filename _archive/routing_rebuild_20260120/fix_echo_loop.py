"""Fix: Keep listening after detecting echo, don't return to wake word"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The current broken pattern
old = '''                if follow_up:
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(follow_up, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, waiting for human...")
                        follow_up = ""
                        command = None
                    else:
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'")
                else:
                    print("[VOICE] No follow-up, back to wake word mode")
                    command = None
                continue'''

# Fixed: check echo inside loop, reset timer, keep listening
new = '''                if follow_up:
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(follow_up, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                        # Reset and keep listening for human
                        follow_up_start = time.time()
                        follow_up = ""
                        continue  # Stay in follow-up mode
                    else:
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'")
                else:
                    print("[VOICE] No follow-up, back to wake word mode")
                    command = None
                continue'''

count = content.count(old)
if count > 0:
    content = content.replace(old, new)
    print(f"✅ Fixed {count} location(s) - echo detection now resets timer")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
