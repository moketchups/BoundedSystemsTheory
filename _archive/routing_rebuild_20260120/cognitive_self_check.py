"""
Demerzel uses her own intelligence to recognize echo.
Before processing follow-up, she asks herself:
"I just said X. I'm now hearing Y. Is this my own echo?"
"""

ECHO_CHECK_PROMPT = """I just spoke the following:
"{spoken}"

Now I'm hearing this audio input:
"{heard}"

Is this input likely MY OWN ECHO being picked up by the microphone, or is this genuinely new input from the human user?

Respond with ONLY one word: ECHO or HUMAN"""

def cognitive_echo_check(cognitive_engine, heard: str, spoken: str) -> bool:
    """Use LLM intelligence to detect echo. Returns True if echo."""
    if not heard or not spoken or len(heard.split()) < 4:
        return False
    
    prompt = ECHO_CHECK_PROMPT.format(spoken=spoken[:500], heard=heard)
    
    try:
        # Quick check - use the cognitive engine
        response = cognitive_engine.quick_check(prompt)
        is_echo = "ECHO" in response.upper()
        if is_echo:
            print(f"[SELF-AWARENESS] I recognize my own echo")
        return is_echo
    except:
        # Fallback to word overlap
        heard_words = set(heard.lower().split())
        spoken_words = set(spoken.lower().split())
        overlap = len(heard_words & spoken_words) / len(heard_words) if heard_words else 0
        return overlap > 0.5

print("✅ Created cognitive_self_check.py")
print("This gives Demerzel real self-awareness through critical thought")
