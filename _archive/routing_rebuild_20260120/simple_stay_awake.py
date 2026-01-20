import re

with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find the main while loop and insert stay-awake logic
new_lines = []
i = 0
while i < len(lines):
    new_lines.append(lines[i])
    
    # After code execution, before continue, add follow-up listener
    if i > 200 and 'continue' in lines[i] and 'Store code error' in ''.join(lines[max(0,i-5):i]):
        # Insert before the continue
        new_lines.pop()  # Remove the continue line
        new_lines.append('\n')
        new_lines.append('                # Stay awake for follow-up\n')
        new_lines.append('                print("[VOICE] Listening for follow-up (no wake word needed)...")\n')
        new_lines.append('                time.sleep(0.5)\n')
        new_lines.append('                follow_up = transcribe_command(recognizer, stream, timeout=4.0)\n')
        new_lines.append('                if follow_up:\n')
        new_lines.append('                    command = follow_up\n')
        new_lines.append('                    # Restart loop with new command\n')
        new_lines.append('                continue\n')
    
    i += 1

with open('brain_controller.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Added simple stay-awake after code execution")
