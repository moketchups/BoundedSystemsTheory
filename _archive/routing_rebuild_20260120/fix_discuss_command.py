"""
Add 'discuss' command for theoretical/philosophical queries
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find available_commands list and add "discuss"
old_commands = '''        self.available_commands = [
            "led on",
            "led off", 
            "time",
            "sleep",
            "ping",
            "execute code",
            "unknown"
        ]'''

new_commands = '''        self.available_commands = [
            "led on",
            "led off", 
            "time",
            "sleep",
            "ping",
            "execute code",
            "discuss",  # For theoretical/philosophical queries
            "unknown"
        ]'''

if old_commands in content:
    content = content.replace(old_commands, new_commands)
    print("✅ Added 'discuss' to available commands")
else:
    print("⚠️ Could not find exact command list - checking alternatives...")
    # Try to find and add anyway
    if '"unknown"' in content and '"discuss"' not in content:
        content = content.replace('"unknown"', '"discuss",\n            "unknown"')
        print("✅ Added 'discuss' command (alternative method)")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
