"""
Add is_awaiting_confirmation method to RouterEngine
"""

with open('router_engine.py', 'r') as f:
    content = f.read()

# Find the class and add method
if 'def is_awaiting_confirmation' not in content:
    # Find a good place to add it - after __init__ or at end of class
    # Look for the class definition
    if 'class RouterEngine' in content:
        # Add method at the end of the class (before last line)
        # Find the last method and add after it
        old_end = '''    def clear_history(self):'''
        new_end = '''    def is_awaiting_confirmation(self):
        """Check if router is waiting for confirmation"""
        return self.state.pending_intent is not None and self.state.confirm_stage > 0
    
    def clear_history(self):'''
        
        if old_end in content:
            content = content.replace(old_end, new_end)
            print("✅ Added is_awaiting_confirmation to RouterEngine")
        else:
            # Try alternate insertion point
            print("⚠️ Could not find clear_history method, trying alternate")
else:
    print("✅ is_awaiting_confirmation already exists")

with open('router_engine.py', 'w') as f:
    f.write(content)
