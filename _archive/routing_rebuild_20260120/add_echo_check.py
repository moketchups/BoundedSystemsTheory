"""
Add the actual echo check before processing follow-up
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

changes = 0

# Find all places where follow-up is processed
# Pattern: print(f"[FOLLOW-UP] Processing: '{text}'"
# We need to add check BEFORE the cognitive processing

old_pattern1 = '''                            print(f"[FOLLOW-UP] Processing: '{text}'"'''

new_pattern1 = '''                            # Demerzel thinks: "Is this my own voice?"
                            if is_likely_echo(text, last_spoken_text):
                                print(f"[SELF-AWARENESS] Ignoring my own echo: '{text[:50]}...'")
                                continue
                            print(f"[FOLLOW-UP] Processing: '{text}'"'''

count1 = content.count(old_pattern1)
if count1 > 0:
    content = content.replace(old_pattern1, new_pattern1)
    changes += count1
    print(f"✅ Added echo check at {count1} locations (4-space indent)")

# Try alternate indent
old_pattern2 = '''                        print(f"[FOLLOW-UP] Processing: '{text}'"'''

new_pattern2 = '''                        # Demerzel thinks: "Is this my own voice?"
                        if is_likely_echo(text, last_spoken_text):
                            print(f"[SELF-AWARENESS] Ignoring my own echo: '{text[:50]}...'")
                            continue
                        print(f"[FOLLOW-UP] Processing: '{text}'"'''

count2 = content.count(old_pattern2)
if count2 > 0:
    content = content.replace(old_pattern2, new_pattern2)
    changes += count2
    print(f"✅ Added echo check at {count2} locations (2-space indent)")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print(f"\n✅ Added {changes} echo checks total")
