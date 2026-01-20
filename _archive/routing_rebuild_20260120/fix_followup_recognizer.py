with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find the follow-up mode section and add recognizer recreation BEFORE it
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Right before follow-up mode, ensure we're using fresh recognizer
    if '[VOICE] Follow-up mode' in line:
        # Insert recognizer check/recreation before this line
        new_lines.append('                # Ensure fresh recognizer for follow-up (no residual buffers)\n')
        new_lines.append('                recognizer = create_recognizer()\n')
        new_lines.append('                print("[VOICE] Fresh recognizer for follow-up")\n')
        new_lines.append('                \n')
    
    new_lines.append(line)
    i += 1

with open('brain_controller.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Added fresh recognizer recreation before follow-up mode")
