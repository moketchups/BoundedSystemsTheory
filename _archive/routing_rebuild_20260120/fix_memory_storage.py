with open('brain_controller.py', 'r') as f:
    content = f.read()

# Fix 1: Add user input storage (it's missing)
old = '''            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)'''

new = '''            print(f"[COGNITIVE] Processing: '{command}'")
            
            # Store user input in memory
            memory.store_conversation("user", command)
            
            # Process through cognitive layer
            cognitive_output = cognitive.process(command)'''

content = content.replace(old, new)

# Fix 2: Add code execution success storage
old = '''                    print(f"[CODE OUTPUT] {output}")
                    speak(tts, f"Code executed successfully. Result: {output[:100]}")'''

new = '''                    print(f"[CODE OUTPUT] {output}")
                    response = f"Code executed successfully. Result: {output[:100]}"
                    speak(tts, response)
                    # Store code execution in memory
                    memory.store_conversation("demerzel", response, 
                                            intent="CODE_EXECUTION",
                                            executed=True)'''

content = content.replace(old, new)

# Fix 3: Add code execution error storage
old = '''                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    speak(tts, f"Code execution failed. {error[:100]}")'''

new = '''                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    response = f"Code execution failed. {error[:100]}"
                    speak(tts, response)
                    # Store code error in memory
                    memory.store_conversation("demerzel", response,
                                            intent="CODE_EXECUTION_ERROR",
                                            executed=False)'''

content = content.replace(old, new)

# Fix 4: Add memory clear on sleep
old = '''            if router_output.sleep_mode:
                print("[COGNITIVE] History cleared")
                cognitive.clear_history()
                speak(tts, "Going to sleep. Wake me when you need me.")'''

new = '''            if router_output.sleep_mode:
                print("[VOICE] Sleep mode activated")
                cognitive.clear_history()
                memory.clear_working_memory()
                speak(tts, "Going to sleep. Wake me when you need me.")'''

content = content.replace(old, new)

# Fix 5: Add session end on exit
old = '''    except KeyboardInterrupt:
        print("\n[VOICE] Shutting down...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Cleanup complete")'''

new = '''    except KeyboardInterrupt:
        print("\n[VOICE] Shutting down...")
    finally:
        memory.end_session()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Cleanup complete")'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed all memory storage hooks")
