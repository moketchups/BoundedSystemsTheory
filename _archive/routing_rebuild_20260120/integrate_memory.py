with open('brain_controller.py', 'r') as f:
    lines = f.readlines()

# Find imports section and add memory import
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'from multi_model_cognitive import MultiModelCognitive' in line:
        new_lines.append('from memory_manager import MemoryManager\n')

# Find router initialization and add memory
output_lines = []
for i, line in enumerate(new_lines):
    output_lines.append(line)
    if 'router = RouterEngine()' in line:
        output_lines.append('    memory = MemoryManager()\n')
        output_lines.append('    print(f"[MEMORY] Initialized")\n')

with open('brain_controller.py', 'w') as f:
    f.writelines(output_lines)

print("Step 1: Added memory initialization")
