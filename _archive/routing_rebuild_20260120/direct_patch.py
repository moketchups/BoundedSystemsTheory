"""
Direct line-by-line patch
"""

with open('multi_model_cognitive.py', 'r') as f:
    lines = f.readlines()

# Insert after line 32 (index 31)
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # After line 32 (self.memory = memory_manager)
    if i == 31:  # 0-indexed, so line 32 is index 31
        new_lines.append('        \n')
        new_lines.append('        # Load theoretical grounding\n')
        new_lines.append('        self.theoretical_context = get_theoretical_context()\n')
        new_lines.append('        print("[COGNITIVE] Theoretical understanding loaded")\n')
        print(f"✅ Inserted theoretical context after line {i+1}")

with open('multi_model_cognitive.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Done")
