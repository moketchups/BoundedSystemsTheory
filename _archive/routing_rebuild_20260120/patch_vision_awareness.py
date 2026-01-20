"""
Add vision-based self-awareness to follow-up mode.
Three-layer detection:
1. is_likely_echo() - text comparison
2. vision.is_human_speaking() - lip detection
3. Combined reasoning
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Replace the first follow-up logic (after normal commands)
old_followup = '''                if follow_up:
                    # Demerzel thinks: "Is this my own voice?"
                    if is_likely_echo(follow_up, last_spoken_text):
                        print(f"[SELF-AWARENESS] Ignoring my echo, waiting for human...")
                        follow_up = ""
                        command = None
                    else:
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'"'''

new_followup = '''                if follow_up:
                    # Multi-modal self-awareness check
                    human_speaking = vision.is_human_speaking() if vision else False
                    echo_detected = is_likely_echo(follow_up, last_spoken_text)
                    
                    if human_speaking:
                        # Camera sees human talking - trust that
                        print(f"[SELF-AWARENESS] Vision confirms human speaking")
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'"
                    elif echo_detected:
                        # No human lips moving + matches my words = my echo
                        print(f"[SELF-AWARENESS] Echo detected (no human lips), ignoring...")
                        follow_up = ""
                        command = None
                    else:
                        # Doesn't match my words, probably human (camera may have missed)
                        command = follow_up
                        print(f"[FOLLOW-UP] Processing: '{command}'"'''

if old_followup in content:
    content = content.replace(old_followup, new_followup)
    print("✅ Updated first follow-up with vision awareness")
else:
    print("❌ First follow-up pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
