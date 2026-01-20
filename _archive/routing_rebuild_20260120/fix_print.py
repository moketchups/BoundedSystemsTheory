import re

# Read the file
with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find the code generation section and add print wrapper
old_pattern = '''                "router_command": "execute code",
                "generated_code": code_block'''

new_pattern = '''                "router_command": "execute code",
                "generated_code": f"result = ({code_block})\\nif result is not None:\\n    print(result)"'''

content = content.replace(old_pattern, new_pattern)

# Write back
with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("Fixed: Code will now print results")
