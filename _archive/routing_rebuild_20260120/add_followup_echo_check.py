"""Add echo check to follow-up mode"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find the follow-up processing and add echo check
old = '''                if follow_up:
                    command = follow_up
                    print(f"[FOLLOW-UP] Processing: '{command}'")'''

new = '''                if follow_up:
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(follow_up, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, waiting for human...")
                        follow_up = ""
                        command = None
                    else:
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'")'''

count = content.count(old)
if count > 0:
    content = content.replace(old, new)
    print(f"✅ Added echo check to {count} follow-up location(s)")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
