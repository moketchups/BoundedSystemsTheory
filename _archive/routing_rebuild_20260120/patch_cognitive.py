# Patch to integrate theoretical context into cognitive layer

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Add import at top
import_line = "from theoretical_context import get_theoretical_context\n"
if import_line not in content:
    # Find first import and add after it
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            lines.insert(i+1, "from theoretical_context import get_theoretical_context")
            break
    content = '\n'.join(lines)

# Modify __init__ to load theoretical context
old_init = '''    def __init__(self, memory_manager: 'MemoryManager' = None):
        self.memory_manager = memory_manager'''

new_init = '''    def __init__(self, memory_manager: 'MemoryManager' = None):
        self.memory_manager = memory_manager
        
        # Load theoretical grounding
        self.theoretical_context = get_theoretical_context()
        print("[COGNITIVE] Theoretical understanding loaded")'''

content = content.replace(old_init, new_init)

# Modify process() to inject theoretical context
old_process_start = '''    def process(self, user_input: str) -> CognitiveOutput:
        """Process user input through cognitive layer"""'''

new_process_start = '''    def process(self, user_input: str) -> CognitiveOutput:
        """Process user input through cognitive layer with theoretical understanding"""
        
        # Check if this is a boundary case
        boundary_check = self.theoretical_context.check_boundary_case(user_input)
        if boundary_check['is_boundary_case']:
            print(f"[COGNITIVE] Boundary case detected - using theoretical understanding")'''

content = content.replace(old_process_start, new_process_start)

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("✅ Patched multi_model_cognitive.py with theoretical context")
