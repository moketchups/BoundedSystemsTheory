"""
Properly integrate theoretical context into cognitive layer
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'theoretical_context' in content:
    print("Already patched - checking if complete...")
    if 'self.theoretical_context = get_theoretical_context()' in content:
        print("✅ Already fully patched")
        exit(0)

# Add import at the top after other imports
if 'from theoretical_context import' not in content:
    # Find the last import statement
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    # Insert after last import
    lines.insert(last_import_idx + 1, 'from theoretical_context import get_theoretical_context')
    content = '\n'.join(lines)
    print("✅ Added import")

# Find the __init__ method and add theoretical context
lines = content.split('\n')
new_lines = []
in_init = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Look for __init__ in MultiModelCognitive class
    if 'def __init__(self' in line and 'MultiModelCognitive' in ''.join(lines[max(0,i-10):i]):
        in_init = True
    
    # Add theoretical context right after memory_manager assignment
    if in_init and 'self.memory_manager = memory_manager' in line:
        new_lines.append('        ')
        new_lines.append('        # Load theoretical grounding')
        new_lines.append('        self.theoretical_context = get_theoretical_context()')
        new_lines.append('        print("[COGNITIVE] Theoretical understanding loaded")')
        in_init = False
        print("✅ Added theoretical context to __init__")

content = '\n'.join(new_lines)

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("✅ Cognitive layer patched successfully")
