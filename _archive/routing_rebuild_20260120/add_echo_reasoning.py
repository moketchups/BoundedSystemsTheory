"""
Add cognitive echo detection before processing follow-up
Demerzel thinks: "Is this my own voice I'm hearing?"
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find where follow-up is processed and add echo check
# Pattern: [FOLLOW-UP] Processing: 
old_process = '''[FOLLOW-UP] Processing: '{text}'"'''

# We need to add a function that does the check
# Add it near the top, after the last_spoken_text declaration

func_marker = '# Track what Demerzel last said (for echo detection)\nlast_spoken_text = ""'
new_func = '''# Track what Demerzel last said (for echo detection)
last_spoken_text = ""

def is_likely_echo(heard: str, spoken: str) -> bool:
    """Demerzel thinks: Is this input likely my own echo?"""
    if not heard or not spoken:
        return False
    
    heard_words = set(heard.lower().split())
    spoken_words = set(spoken.lower().split())
    
    if len(heard_words) < 3:
        return False
    
    # What fraction of heard words appear in what I just said?
    overlap = len(heard_words & spoken_words)
    ratio = overlap / len(heard_words)
    
    if ratio > 0.5:  # More than half the words match what I said
        print(f"[ECHO DETECTED] {overlap}/{len(heard_words)} words match my last response")
        return True
    return False'''

if func_marker in content:
    content = content.replace(func_marker, new_func)
    print("✅ Added is_likely_echo() function")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ Step 2 complete: Added echo detection logic")
