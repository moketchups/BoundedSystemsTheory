"""
Fix TTS gate checks and set Yeti Nano mic
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

changes = 0

# 1. Fix main recognition (line 144 area)
old_main = '''            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0.0):.2f})")
                all_text.append(text)'''

new_main = '''            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0.0):.2f})")
                
                # TTS Gate: ignore Demerzel's own voice
                if not tts_gate.should_process_audio():
                    print(f"[TTS GATE] Ignoring echo: '{text}'")
                    continue
                    
                all_text.append(text)'''

if old_main in content:
    content = content.replace(old_main, new_main)
    changes += 1
    print("✅ Fixed main recognition gate check")
else:
    print("❌ Could not find main recognition pattern")

# 2. Fix follow-up recognitions (3 locations)
old_followup = '''                        if text:
                            follow_up = text
                            print(f"[FOLLOW-UP] Got: '{text}'")
                            break'''

new_followup = '''                        if text:
                            # TTS Gate: ignore Demerzel's own voice
                            if not tts_gate.should_process_audio():
                                print(f"[TTS GATE] Ignoring follow-up echo: '{text}'")
                                continue
                            follow_up = text
                            print(f"[FOLLOW-UP] Got: '{text}'")
                            break'''

count = content.count(old_followup)
if count > 0:
    content = content.replace(old_followup, new_followup)
    changes += count
    print(f"✅ Fixed {count} follow-up recognition gate checks (4-space indent)")

# Try 2-space indent version too
old_followup2 = '''                    if text:
                        follow_up = text
                        print(f"[FOLLOW-UP] Got: '{text}'")
                        break'''

new_followup2 = '''                    if text:
                        # TTS Gate: ignore Demerzel's own voice
                        if not tts_gate.should_process_audio():
                            print(f"[TTS GATE] Ignoring follow-up echo: '{text}'")
                            continue
                        follow_up = text
                        print(f"[FOLLOW-UP] Got: '{text}'")
                        break'''

count2 = content.count(old_followup2)
if count2 > 0:
    content = content.replace(old_followup2, new_followup2)
    changes += count2
    print(f"✅ Fixed {count2} follow-up recognition gate checks (2-space indent)")

# 3. Set Yeti Nano as mic (device_index=1)
# Find where PyAudio stream is opened
old_stream = '''    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=4096)'''

new_stream = '''    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=1,  # Yeti Nano
                    frames_per_buffer=4096)'''

if old_stream in content:
    content = content.replace(old_stream, new_stream)
    changes += 1
    print("✅ Set Yeti Nano as input device (index=1)")
else:
    # Try alternate pattern
    if 'input_device_index' not in content and 'p.open(' in content:
        print("⚠️ PyAudio stream pattern different, checking...")
        import re
        match = re.search(r'stream = p\.open\([^)]+\)', content, re.DOTALL)
        if match:
            print(f"   Found: {match.group(0)[:100]}...")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print(f"\n✅ Made {changes} changes total")
