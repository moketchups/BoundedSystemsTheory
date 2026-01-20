with open('multi_model_cognitive.py', 'r') as f:
    lines = f.readlines()

# Find line 269 (index 268) and replace
for i, line in enumerate(lines):
    if i == 268 and 'generated_code=generated_code' in line:
        # Add wrapper to print expression results
        lines[i] = '                generated_code=f"__result__ = ({generated_code})\\nif __result__ is not None:\\n    print(__result__)" if generated_code and not "print(" in generated_code else generated_code\n'
        break

with open('multi_model_cognitive.py', 'w') as f:
    f.writelines(lines)

print("Fixed: Expressions will now print results")
