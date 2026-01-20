with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find the stay-awake section and improve it
new_lines = []
for i, line in enumerate(lines):
    # Replace the follow-up listener to be more explicit
    if '[VOICE] Listening for follow-up' in line:
        # Remove this section and replace with better version
        new_lines.append('                # Stay awake - listen for follow-up WITHOUT wake word detection\n')
        new_lines.append('                print("[VOICE] Ready for follow-up (no wake word needed)...")\n')
        new_lines.append('                time.sleep(0.3)  # Brief pause\n')
        new_lines.append('                \n')
        new_lines.append('                # Get follow-up directly (no wake word check)\n')
        new_lines.append('                follow_up = transcribe_command(recognizer, stream, timeout=5.0)\n')
        new_lines.append('                if follow_up:\n')
        new_lines.append('                    command = follow_up\n')
        new_lines.append('                    print(f"[FOLLOW-UP] Processing: \'{command}\'")\n')
        new_lines.append('                    # Loop back to process this command\n')
        new_lines.append('                continue\n')
        
        # Skip the old implementation
        while i < len(lines) and 'continue' not in lines[i]:
            i += 1
        continue
    else:
        new_lines.append(line)

with open('brain_controller.py', 'w') as f:
    f.writelines(new_lines)

print("Step 2: Fixed follow-up to skip wake word detection")
