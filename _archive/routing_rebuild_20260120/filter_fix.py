with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find and replace the output handling section
new_lines = []
i = 0
while i < len(lines):
    if 'output = result.stdout.strip() or "(no output)"' in lines[i]:
        # Replace the next few lines
        new_lines.append('                    # Filter out file system debug messages\n')
        new_lines.append('                    lines = result.stdout.strip().split("\\n")\n')
        new_lines.append('                    output_lines = [l for l in lines if not l.startswith("[FILE SYSTEM]")]\n')
        new_lines.append('                    output = "\\n".join(output_lines).strip() or "(no output)"\n')
        i += 1  # Skip the original line
    else:
        new_lines.append(lines[i])
        i += 1

with open('brain_controller.py', 'w') as f:
    f.writelines(new_lines)

print("Fixed: File system messages filtered from output")
