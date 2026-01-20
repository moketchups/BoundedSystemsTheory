"""
Add DISCUSS intent to handle theoretical queries
"""

# 1. Add to Intent enum in kernel_contract.py
with open('kernel_contract.py', 'r') as f:
    content = f.read()

old_enum = '''class Intent(Enum):
    UNKNOWN = auto()
    PING = auto()
    LED_ON = auto()
    LED_OFF = auto()
    TIME = auto()
    SLEEP = auto()
    CANCEL = auto()
    EXECUTE_CODE = auto()'''

new_enum = '''class Intent(Enum):
    UNKNOWN = auto()
    PING = auto()
    LED_ON = auto()
    LED_OFF = auto()
    TIME = auto()
    SLEEP = auto()
    CANCEL = auto()
    EXECUTE_CODE = auto()
    DISCUSS = auto()  # Theoretical/philosophical queries'''

if old_enum in content:
    content = content.replace(old_enum, new_enum)
    with open('kernel_contract.py', 'w') as f:
        f.write(content)
    print("✅ Added DISCUSS to Intent enum")
else:
    if 'DISCUSS = auto()' in content:
        print("✅ DISCUSS already in Intent enum")
    else:
        print("⚠️ Could not find exact Intent enum")

# 2. Add to _intent_from_text in kernel_router.py
with open('kernel_router.py', 'r') as f:
    content = f.read()

# Find where we return UNKNOWN at the end and add discuss before it
old_return = '''    return Intent.UNKNOWN, ""'''

# First, add discuss detection before the final return
if 'discuss' not in content.lower() or '"discuss"' not in content:
    # Find the _intent_from_text function and add discuss handling
    old_time = '''if "time" in t or "what time" in t:'''
    new_time = '''if "discuss" in t:
        return Intent.DISCUSS, ""
    if "time" in t or "what time" in t:'''
    
    if old_time in content and 'if "discuss" in t:' not in content:
        content = content.replace(old_time, new_time)
        print("✅ Added discuss detection to _intent_from_text")
    else:
        print("⚠️ Could not add discuss detection")
else:
    print("✅ discuss detection already exists")

with open('kernel_router.py', 'w') as f:
    f.write(content)

print("✅ Intent patches complete")
