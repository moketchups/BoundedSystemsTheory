with open('brain_controller.py', 'r') as f:
    content = f.read()

# Update cognitive initialization to receive memory
old = '''    # Initialize cognitive and router
    cognitive = MultiModelCognitive()
    router = RouterEngine()
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")'''

new = '''    # Initialize memory first
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    
    # Initialize cognitive with memory
    cognitive = MultiModelCognitive(memory_manager=memory)
    router = RouterEngine()'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Connected memory to cognitive layer")
