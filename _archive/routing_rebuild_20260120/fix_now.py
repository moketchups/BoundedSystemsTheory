"""
Fix the transcribe_command bug - it hears text but doesn't return it
"""
with open('brain_controller.py', 'r') as f:
    content = f.read()

# The bug: prints [HEARD] but checks "if not partial_text" before returning
# This means if there's ANY partial text, it ignores valid heard results

old_bug = '''        # Also check AcceptWaveform but don't trust it alone
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}'")
                # Only use this if partials are empty (speaker stopped)
                if not partial_text:
                    print(f"[FULL COMMAND] '{text}'")
                    return text'''

fix = '''        # When Vosk finalizes text, RETURN IT
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[COMMAND] '{text}'")
                return text'''

if old_bug in content:
    content = content.replace(old_bug, fix)
    print("✅ Fixed transcribe_command")
else:
    print("❌ Pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
