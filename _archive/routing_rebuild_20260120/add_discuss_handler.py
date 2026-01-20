"""
Add DISCUSS handler to route function
"""

with open('kernel_router.py', 'r') as f:
    content = f.read()

# Find where we handle intents and add DISCUSS handler
# Look for the pattern where we check intent types

# First, check if there's a section handling EXECUTE_CODE
if 'Intent.EXECUTE_CODE' in content and 'Intent.DISCUSS' not in content:
    # Add DISCUSS handling after EXECUTE_CODE handling
    old_pattern = '''    if intent == Intent.EXECUTE_CODE:'''
    
    # Find the execute code section and add discuss after it
    # We need to find a good insertion point
    
    # Let's look for the fallback to UNKNOWN
    old_fallback = '''    return RouterOutput(speak="I don't understand that command.", intent=Intent.UNKNOWN), st'''
    
    new_fallback = '''    # Handle DISCUSS intent - speak the discussion
    if intent == Intent.DISCUSS:
        # Discussion is handled by speaking the response
        return RouterOutput(speak="", intent=Intent.DISCUSS, did_execute=True), st
    
    return RouterOutput(speak="I don't understand that command.", intent=Intent.UNKNOWN), st'''
    
    if old_fallback in content:
        content = content.replace(old_fallback, new_fallback)
        print("✅ Added DISCUSS handler before UNKNOWN fallback")
    else:
        print("⚠️ Could not find fallback pattern")
else:
    if 'Intent.DISCUSS' in content:
        print("✅ DISCUSS handler already exists")
    else:
        print("⚠️ Could not add DISCUSS handler")

with open('kernel_router.py', 'w') as f:
    f.write(content)
