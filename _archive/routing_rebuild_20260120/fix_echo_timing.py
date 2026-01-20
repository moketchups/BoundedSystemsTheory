with open('brain_controller.py', 'r') as f:
    content = f.read()

# Increase wait time in speak function
old = '''    # Wait for acoustic echo to dissipate
    time.sleep(1.2)'''

new = '''    # Wait for acoustic echo to FULLY dissipate
    time.sleep(2.5)  # Longer wait for room acoustics'''

content = content.replace(old, new)

# Also add extra wait BEFORE follow-up mode
old = '''                # Follow-up mode with fresh recognizer
                recognizer = create_recognizer()
                print("[VOICE] Follow-up mode (5 sec, speak now)...")'''

new = '''                # Follow-up mode with fresh recognizer
                recognizer = create_recognizer()
                
                # Extra wait to ensure ALL acoustic echo is gone
                time.sleep(1.0)
                print("[VOICE] Follow-up mode (5 sec, speak now)...")'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Increased acoustic echo wait times")
