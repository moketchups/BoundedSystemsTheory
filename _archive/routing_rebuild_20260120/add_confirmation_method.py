"""
Add is_awaiting_confirmation method to RouterEngine - find correct insertion point
"""

with open('router_engine.py', 'r') as f:
    content = f.read()

# The class ends after _handle_code_execution
# Add method before the last closing of the class

# Find the last return statement in _handle_code_execution
old_end = '''        return replace(
            out,
            speak=speak,
            did_execute=True,
            error=result.stderr if not result.success else None
        )'''

new_end = '''        return replace(
            out,
            speak=speak,
            did_execute=True,
            error=result.stderr if not result.success else None
        )
    
    def is_awaiting_confirmation(self):
        """Check if router is waiting for confirmation"""
        return self.state.pending_intent is not None and self.state.confirm_stage > 0'''

if old_end in content and 'def is_awaiting_confirmation' not in content:
    content = content.replace(old_end, new_end)
    print("✅ Added is_awaiting_confirmation to RouterEngine")
else:
    if 'def is_awaiting_confirmation' in content:
        print("✅ is_awaiting_confirmation already exists")
    else:
        print("⚠️ Could not find insertion point")

with open('router_engine.py', 'w') as f:
    f.write(content)
