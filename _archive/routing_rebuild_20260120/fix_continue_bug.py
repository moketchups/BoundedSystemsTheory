"""
Fix the continue bug - need to skip ALL processing, not just continue loop
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# The issue: continue doesn't prevent processing
# Fix: Use else clause to ensure processing only happens if NOT echo

# Pattern 1 (20-space indent)
old1 = '''                if follow_up:
                    command = follow_up
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my own echo: '{command[:50]}...'")
                        follow_up = ""
                        continue
                    print(f"[FOLLOW-UP] Processing: '{command}'")'''

new1 = '''                if follow_up:
                    command = follow_up
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(command, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring - this is my own echo")
                        command = ""  # Clear so nothing processes
                        follow_up = ""
                
                if follow_up and command:  # Only process if not echo
                    print(f"[FOLLOW-UP] Processing: '{command}'")'''

content = content.replace(old1, new1)

# Pattern 2 (12-space indent)  
old2 = '''            if follow_up:
                command = follow_up
                # Demerzel thinks: "Is this my own voice?"
                if is_likely_echo(command, last_spoken_text):
                    print(f"[SELF-AWARENESS] Ignoring my own echo: '{command[:50]}...'")
                    follow_up = ""
                    continue
                print(f"[FOLLOW-UP] Processing: '{command}'")'''

new2 = '''            if follow_up:
                command = follow_up
                # Demerzel thinks: "Is this my own voice?"
                if is_likely_echo(command, last_spoken_text):
                    print(f"[SELF-AWARENESS] Ignoring - this is my own echo")
                    command = ""
                    follow_up = ""
            
            if follow_up and command:  # Only process if not echo
                print(f"[FOLLOW-UP] Processing: '{command}'")'''

content = content.replace(old2, new2)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed continue bug - now clears command to prevent ALL processing")
