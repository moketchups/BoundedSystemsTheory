"""
Integrate TTSGate into brain_controller for echo suppression
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# 1. Add import
old_import = '''from vision_filter import VisionFilter'''
new_import = '''from vision_filter import VisionFilter
from tts_gate import TTSGate'''

if old_import in content:
    content = content.replace(old_import, new_import)
    print("✅ Added TTSGate import")
else:
    # Try adding after multi_model import
    old_import2 = '''from multi_model_cognitive import MultiModelCognitive'''
    new_import2 = '''from multi_model_cognitive import MultiModelCognitive
from tts_gate import TTSGate'''
    content = content.replace(old_import2, new_import2)
    print("✅ Added TTSGate import (alt location)")

# 2. Initialize TTSGate near the top of voice_mode
old_init = '''    # Vision filter for echo suppression
    vision = VisionFilter'''
new_init = '''    # TTS Gate for echo suppression (deterministic)
    tts_gate = TTSGate(post_speech_buffer=0.8)
    print("[TTS GATE] Initialized (0.8s buffer)")
    
    # Vision filter for echo suppression
    vision = VisionFilter'''

if old_init in content:
    content = content.replace(old_init, new_init)
    print("✅ Added TTSGate initialization")
else:
    print("⚠️ Could not find vision init, trying alternate")
    # Try alternate location
    old_init2 = '''    router = RouterEngine()
    analyzer = CodeAnalyzer()'''
    new_init2 = '''    router = RouterEngine()
    analyzer = CodeAnalyzer()
    
    # TTS Gate for echo suppression (deterministic)
    tts_gate = TTSGate(post_speech_buffer=0.8)
    print("[TTS GATE] Initialized (0.8s buffer)")'''
    content = content.replace(old_init2, new_init2)
    print("✅ Added TTSGate initialization (alt location)")

# 3. Wrap speak() calls with gate
# Find the speak function usage and wrap it
# We need to modify the speak call pattern

# Look for the speak wrapper or create hooks
# The key is: before speak() -> gate.start_speaking(), after -> gate.stop_speaking()

# Let's find how speak is used
if 'def speak(' in content:
    print("✅ Found speak function definition")
    
    # We'll modify the speak function itself to include gating
    old_speak_start = '''def speak(text: str):
    """Speak text using macOS say command"""
    print(f"[SPEAK] {text}")'''
    
    new_speak_start = '''def speak(text: str, gate: TTSGate = None):
    """Speak text using macOS say command with TTS gating"""
    print(f"[SPEAK] {text}")
    if gate:
        gate.start_speaking()'''
    
    if old_speak_start in content:
        content = content.replace(old_speak_start, new_speak_start)
        print("✅ Modified speak() to accept gate parameter")
    else:
        print("⚠️ speak() signature different, checking...")

# Add gate.stop_speaking() after subprocess in speak
old_speak_end = '''        subprocess.run(['say', '-v', 'Samantha', text], check=True)
    except Exception as e:
        print(f"[SPEAK ERROR] {e}")'''

new_speak_end = '''        subprocess.run(['say', '-v', 'Samantha', text], check=True)
        if gate:
            gate.stop_speaking()
    except Exception as e:
        print(f"[SPEAK ERROR] {e}")
        if gate:
            gate.stop_speaking()'''

if old_speak_end in content:
    content = content.replace(old_speak_end, new_speak_end)
    print("✅ Added gate.stop_speaking() after TTS")
else:
    print("⚠️ Could not find speak subprocess pattern")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ TTSGate integrated!")
print("\nNext: Need to pass tts_gate to speak() calls and check should_process_audio()")
