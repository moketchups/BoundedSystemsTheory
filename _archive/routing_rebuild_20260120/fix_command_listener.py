"""
Fix: Trust partials, not AcceptWaveform timing.
Only finalize when partials have been STABLE for 1.5 seconds.
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

old_transcribe = '''def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 8.0) -> str:
    """Transcribe user command with longer timeout and better aggregation"""
    print("[COGNITIVE] Listening for command...")
    start_time = time.time()
    all_text = []
    
    while time.time() - start_time < timeout:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}' (conf={result.get('confidence', 0.0):.2f})")
                all_text.append(text)
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text:
                print(f"[PARTIAL] '{partial_text}'")
    
    # Combine all recognized text
    full_command = " ".join(all_text).strip()
    if full_command:
        print(f"[FULL COMMAND] '{full_command}'")
    return full_command'''

new_transcribe = '''def transcribe_command(recognizer: KaldiRecognizer, stream, timeout: float = 10.0) -> str:
    """
    Transcribe user command - TRUST PARTIALS, not AcceptWaveform timing.
    Only finalize when partials have been STABLE for 1.5 seconds.
    """
    print("[COGNITIVE] Listening for command...")
    start_time = time.time()
    
    last_partial = ""
    last_partial_time = time.time()
    stable_threshold = 1.5  # Seconds of stability before finalizing
    
    while time.time() - start_time < timeout:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Check partial results - this is our source of truth
        partial = json.loads(recognizer.PartialResult())
        partial_text = partial.get("partial", "").strip()
        
        if partial_text != last_partial:
            # Partial changed - reset stability timer
            if partial_text:
                print(f"[PARTIAL] '{partial_text}'")
            last_partial = partial_text
            last_partial_time = time.time()
        
        # Check if partials have been stable long enough
        if last_partial and (time.time() - last_partial_time) >= stable_threshold:
            # Force finalization
            final = json.loads(recognizer.FinalResult())
            final_text = final.get("text", "").strip()
            
            # Use whichever is longer/better - final or last stable partial
            command = final_text if len(final_text) >= len(last_partial) else last_partial
            if command:
                print(f"[STABLE] '{command}'")
                return command
        
        # Also check AcceptWaveform but don't trust it alone
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"[HEARD] '{text}'")
                # Only use this if partials are empty (speaker stopped)
                if not partial_text:
                    print(f"[FULL COMMAND] '{text}'")
                    return text
    
    # Timeout - use whatever we have
    if last_partial:
        final = json.loads(recognizer.FinalResult())
        final_text = final.get("text", "").strip()
        command = final_text if len(final_text) >= len(last_partial) else last_partial
        if command:
            print(f"[TIMEOUT] '{command}'")
            return command
    
    return ""'''

if old_transcribe in content:
    content = content.replace(old_transcribe, new_transcribe)
    print("✅ Replaced transcribe_command with partial-stable version")
else:
    print("❌ transcribe_command pattern not found")

with open('brain_controller.py', 'w') as f:
    f.write(content)
