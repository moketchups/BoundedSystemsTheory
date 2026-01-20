"""Add echo detection to brain_controller"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find a good insertion point - after CHUNK constant
marker = 'CHUNK = 4096'
echo_code = '''CHUNK = 4096

# Track what Demerzel last said (for echo detection)
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
    
    if ratio > 0.5:
        print(f"[SELF-AWARENESS] Echo detected - {overlap}/{len(heard_words)} words match my speech")
        return True
    return False'''

if marker in content and 'last_spoken_text' not in content:
    content = content.replace(marker, echo_code)
    print("✅ Added last_spoken_text and is_likely_echo()")
else:
    print("⚠️ Already has echo detection or marker not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
