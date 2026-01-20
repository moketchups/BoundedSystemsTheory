"""
Add discuss handling to brain_controller
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Find where we route to kernel and add discuss handling before it
old_route = '''            router_output = router.route_text(cognitive_output.router_command)'''

new_route = '''            # Handle discuss command - speak the discussion directly
            if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
                print(f"[DISCUSS] Speaking theoretical response...")
                speak(tts, cognitive_output.discussion, stream)
                recognizer = create_recognizer()  # Fresh recognizer after TTS
                memory.store_conversation("demerzel", cognitive_output.discussion,
                                        intent="DISCUSS")
                continue
            
            router_output = router.route_text(cognitive_output.router_command)'''

if old_route in content and 'router_command == "discuss"' not in content:
    content = content.replace(old_route, new_route)
    print("✅ Added discuss handling to brain_controller")
else:
    if 'router_command == "discuss"' in content:
        print("✅ discuss handling already exists")
    else:
        print("⚠️ Could not find route pattern")

with open('brain_controller.py', 'w') as f:
    f.write(content)
