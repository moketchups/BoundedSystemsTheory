"""
After ignoring echo, keep listening for real follow-up
Don't exit to wake mode just because we heard our own voice
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The issue: after echo detection, follow_up="" causes "No follow-up, back to wake mode"
# Fix: Don't clear follow_up immediately - let the loop continue listening

# Pattern 1 (20-space indent)
old1 = '''                if follow_up:
                    command = follow_up
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring - this is my own echo")
                        command = ""  # Clear so nothing processes
                        follow_up = ""'''

new1 = '''                if follow_up:
                    command = follow_up
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                        command = ""
                        follow_up = ""
                        # Reset and keep listening for real input
                        recognizer = create_recognizer()
                        follow_up_start = time.time()  # Reset timer
                        continue  # Stay in follow-up loop'''

content = content.replace(old1, new1)

# Pattern 2 (12-space indent)
old2 = '''            if follow_up:
                command = follow_up
                # Demerzel thinks: "Is this my own voice?"
                if is_likely_echo(command, last_spoken_text):
                    print(f"[SELF-AWARENESS] Ignoring - this is my own echo")
                    command = ""
                    follow_up = ""'''

new2 = '''            if follow_up:
                command = follow_up
                # Demerzel thinks: "Is this my own voice?"
                if is_likely_echo(command, last_spoken_text):
                    print(f"[SELF-AWARENESS] Ignoring my echo, still listening...")
                    command = ""
                    follow_up = ""
                    # Reset and keep listening for real input
                    recognizer = create_recognizer()
                    follow_up_start = time.time()
                    continue'''

content = content.replace(old2, new2)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed: After ignoring echo, Demerzel keeps listening for real follow-up")
