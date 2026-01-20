"""
Fix the broken lines in multi_model_cognitive.py
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Fix 1: The broken router_command line
old_broken = '''router_command=data.get("router_command", "discuss",
            "unknown")'''
new_fixed = '''router_command=data.get("router_command", "unknown")'''

content = content.replace(old_broken, new_fixed)
print("✅ Fixed router_command data.get()")

# Fix 2: The error handler missing router_command
old_error = '''return CognitiveOutput(
                understood_intent="Error processing request",
                explanation=f"Model {model} failed: {str(e)}"
            )'''

new_error = '''return CognitiveOutput(
                understood_intent="Error processing request",
                router_command="unknown",
                explanation=f"Model {model} failed: {str(e)}"
            )'''

content = content.replace(old_error, new_error)
print("✅ Fixed error handler CognitiveOutput")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("✅ All fixes applied")
