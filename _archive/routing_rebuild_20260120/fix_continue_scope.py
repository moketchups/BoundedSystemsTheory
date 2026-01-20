"""
Fix the continue statements - they need to break out of echo_retry loop
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The issue: continue is continuing echo_retry loop, not main loop
# Fix: use break to exit echo_retry, then continue main loop

old = '''                    if follow_up:
                        # Demerzel thinks: "Is this my own voice?"
                        if is_likely_echo(follow_up, last_spoken_text):
                            print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                            recognizer = create_recognizer()
                            echo_retry = True  # Try again
                            continue
                        command = follow_up
                        continue
                    else:
                        command = None
                        continue'''

new = '''                    if follow_up:
                        # Demerzel thinks: "Is this my own voice?"
                        if is_likely_echo(follow_up, last_spoken_text):
                            print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                            recognizer = create_recognizer()
                            echo_retry = True  # Try again
                            continue
                        command = follow_up
                        break  # Exit echo_retry loop with command
                    else:
                        command = None
                        break  # Exit echo_retry loop, no command
                
                # Now continue main loop with command (or None)
                if command:
                    continue
                else:
                    print("[VOICE] No follow-up, back to wake mode")
                    command = None'''

if old in content:
    content = content.replace(old, new)
    print("✅ Fixed continue scope")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
