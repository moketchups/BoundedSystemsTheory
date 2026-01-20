with open('multi_model_cognitive.py', 'r') as f:
    lines = f.readlines()

# Find and simplify the wrapper section
new_lines = []
skip_until_generated_code = False
for i, line in enumerate(lines):
    if '# Smart wrapper:' in line:
        skip_until_generated_code = True
        new_lines.append('                generated_code=generated_code\n')
        continue
    if skip_until_generated_code:
        if 'generated_code=generated_code' in line:
            skip_until_generated_code = False
        continue
    new_lines.append(line)

with open('multi_model_cognitive.py', 'w') as f:
    f.writelines(new_lines)

print("Removed wrapper - LLM will handle printing")
