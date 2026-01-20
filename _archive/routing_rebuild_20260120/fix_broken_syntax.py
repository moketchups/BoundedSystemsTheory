"""
Fix the broken syntax in multi_model_cognitive.py
"""

with open('multi_model_cognitive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Fix the broken router_command line
    if 'router_command="discuss",' in line and i+1 < len(lines) and '"unknown",' in lines[i+1]:
        # Replace with correct line
        new_lines.append(line.replace('router_command="discuss",', 'router_command="unknown",'))
        skip_next = True  # Skip the next line (the broken "unknown",)
        print(f"✅ Fixed broken syntax at line {i+1}")
    else:
        new_lines.append(line)

with open('multi_model_cognitive.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Syntax fix complete")
