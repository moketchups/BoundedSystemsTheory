with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find and replace the entire broken follow-up section
new_lines = []
i = 0
while i < len(lines):
    # Find the start of the broken follow-up section
    if i < len(lines) and 'Ensure fresh recognizer for follow-up' in lines[i]:
        # Skip all the broken follow-up code (lines 275-307)
        # Replace with working version
        new_lines.append('                # Follow-up mode with fresh recognizer\n')
        new_lines.append('                recognizer = create_recognizer()\n')
        new_lines.append('                print("[VOICE] Follow-up mode (5 sec, speak now)...")\n')
        new_lines.append('                \n')
        new_lines.append('                # Listen for follow-up with partial detection\n')
        new_lines.append('                follow_up_start = time.time()\n')
        new_lines.append('                follow_up = ""\n')
        new_lines.append('                partial_detected = False\n')
        new_lines.append('                \n')
        new_lines.append('                while time.time() - follow_up_start < 5.0:\n')
        new_lines.append('                    data = stream.read(CHUNK, exception_on_overflow=False)\n')
        new_lines.append('                    \n')
        new_lines.append('                    if recognizer.AcceptWaveform(data):\n')
        new_lines.append('                        result = json.loads(recognizer.Result())\n')
        new_lines.append('                        text = result.get("text", "").strip()\n')
        new_lines.append('                        if text:\n')
        new_lines.append('                            follow_up = text\n')
        new_lines.append('                            print(f"[FOLLOW-UP] Got: \'{text}\'")\n')
        new_lines.append('                            break\n')
        new_lines.append('                    else:\n')
        new_lines.append('                        partial = json.loads(recognizer.PartialResult())\n')
        new_lines.append('                        partial_text = partial.get("partial", "").strip()\n')
        new_lines.append('                        if partial_text and not partial_detected:\n')
        new_lines.append('                            partial_detected = True\n')
        new_lines.append('                            print(f"[FOLLOW-UP] Hearing: \'{partial_text}...\'")\n')
        new_lines.append('                \n')
        new_lines.append('                # Get final result if we detected speech\n')
        new_lines.append('                if partial_detected and not follow_up:\n')
        new_lines.append('                    final = json.loads(recognizer.FinalResult())\n')
        new_lines.append('                    follow_up = final.get("text", "").strip()\n')
        new_lines.append('                    if follow_up:\n')
        new_lines.append('                        print(f"[FOLLOW-UP] Final: \'{follow_up}\'")\n')
        new_lines.append('                \n')
        new_lines.append('                if follow_up:\n')
        new_lines.append('                    command = follow_up\n')
        new_lines.append('                    print(f"[FOLLOW-UP] Processing: \'{command}\'")\n')
        new_lines.append('                    continue\n')
        new_lines.append('                else:\n')
        new_lines.append('                    print("[VOICE] No follow-up, back to wake mode")\n')
        new_lines.append('                    continue\n')
        
        # Skip to the next section (after all the broken code)
        while i < len(lines) and 'Route command through kernel' not in lines[i]:
            i += 1
        continue
    
    new_lines.append(lines[i])
    i += 1

with open('brain_controller.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed follow-up section completely")
