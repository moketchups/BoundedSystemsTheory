"""
Fix: Drain buffer MORE aggressively before follow-up mode
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Fix the follow-up after discuss - add extra buffer drain
old_followup_discuss = '''                # Follow-up mode after discuss
                time.sleep(0.5)
                print("[VOICE] Follow-up mode (5 sec)...")'''

new_followup_discuss = '''                # Follow-up mode after discuss
                # EXTRA buffer draining to avoid hearing own echo
                time.sleep(1.5)  # Wait for room acoustics
                for _ in range(10):
                    try:
                        stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)
                    except:
                        pass
                recognizer = create_recognizer()  # Fresh recognizer
                print("[VOICE] Follow-up mode (5 sec)...")'''

content = content.replace(old_followup_discuss, new_followup_discuss)
print("✅ Fixed echo drain in discuss follow-up")

# Fix the follow-up after router - add extra buffer drain
old_followup_router = '''            # Follow-up mode after router response (for confirmations, etc.)
            recognizer = create_recognizer()
            time.sleep(0.5)
            print("[VOICE] Follow-up mode (5 sec)...")'''

new_followup_router = '''            # Follow-up mode after router response (for confirmations, etc.)
            # EXTRA buffer draining to avoid hearing own echo
            time.sleep(1.5)  # Wait for room acoustics
            for _ in range(10):
                try:
                    stream.read(int(SAMPLE_RATE * 0.2), exception_on_overflow=False)
                except:
                    pass
            recognizer = create_recognizer()
            print("[VOICE] Follow-up mode (5 sec)...")'''

content = content.replace(old_followup_router, new_followup_router)
print("✅ Fixed echo drain in router follow-up")

with open('brain_controller.py', 'w') as f:
    f.write(content)
