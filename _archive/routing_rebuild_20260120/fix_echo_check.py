"""
Add echo check at the actual locations
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

changes = 0

# Pattern 1 & 2 (lines 466, 530) - 20 spaces indent
old1 = '''                if follow_up:
                    command = follow_up
                    print(f"[FOLLOW-UP] Processing: '{command}'")'''

new1 = '''                if follow_up:
                    command = follow_up
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my own echo: '{command[:50]}...'")
                        follow_up = ""
                        continue
                    print(f"[FOLLOW-UP] Processing: '{command}'")'''

count1 = content.count(old1)
if count1 > 0:
    content = content.replace(old1, new1)
    changes += count1
    print(f"✅ Added echo check at {count1} locations (20-space indent)")

# Pattern 3 (line 597) - 12 spaces indent
old2 = '''            if follow_up:
                command = follow_up
                print(f"[FOLLOW-UP] Processing: '{command}'")'''

new2 = '''            if follow_up:
                command = follow_up
                # Demerzel thinks: "Is this my own voice?"
                if is_likely_echo(command, last_spoken_text):
                    print(f"[SELF-AWARENESS] Ignoring my own echo: '{command[:50]}...'")
                    follow_up = ""
                    continue
                print(f"[FOLLOW-UP] Processing: '{command}'")'''

count2 = content.count(old2)
if count2 > 0:
    content = content.replace(old2, new2)
    changes += count2
    print(f"✅ Added echo check at {count2} locations (12-space indent)")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print(f"\n✅ Added {changes} echo checks total")
