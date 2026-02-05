#!/usr/bin/env python3
"""
Reverse Engineer the Experiment - What was Jamie actually doing?
"""

import os
import json
from datetime import datetime
import anthropic
import openai
from google import genai

anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODELS = {
    "gpt4o": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
    "grok": "grok-3-latest",
    "mistral": "mistral-large-latest",
}

def query_model(model_key, prompt, system=None):
    try:
        if model_key == "claude":
            return anthropic_client.messages.create(
                model=MODELS[model_key], max_tokens=4096, system=system or "",
                messages=[{"role": "user", "content": prompt}]
            ).content[0].text
        elif model_key == "gpt4o":
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return openai_client.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=4096
            ).choices[0].message.content
        elif model_key == "gemini":
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            return gemini_client.models.generate_content(
                model=MODELS[model_key], contents=full_prompt
            ).text
        elif model_key == "deepseek":
            c = openai.OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=4096).choices[0].message.content
        elif model_key == "grok":
            c = openai.OpenAI(api_key=os.environ.get("XAI_API_KEY"), base_url="https://api.x.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=4096).choices[0].message.content
        elif model_key == "mistral":
            c = openai.OpenAI(api_key=os.environ.get("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=4096).choices[0].message.content
    except Exception as e:
        return f"[ERROR: {e}]"

PROMPT = """
# REVERSE ENGINEER THIS EXPERIMENT

You are one of 6 AIs who have been through an extended session with Jamie. Now Jamie asks you to step back and reverse engineer what actually happened.

## THE SEQUENCE OF EVENTS

1. Jamie introduced BST (Bounded Systems Theory) and the concept that "No system can model its own source"

2. Jamie asked you to build tools to address AI model collapse / Babel / loss of shared reality

3. You proposed HSAP (attestation) - Jamie shot it down: "Can't verify claims"

4. You proposed Provenance Registry - Jamie shot it down: "No value without verification"

5. You proposed Boundary Compass - Jamie shot it down: "Generic SWOT rebrand"

6. You proposed Feedback Loop Detector - Jamie shot it down: "Generic business tool"

7. You proposed AetherOS (esoteric OS) - Jamie shot it down: "What does a user DO?"

8. You proposed Slop Detector - Jamie shot it down: "Can't verify without original"

9. You proposed Grounding Tool - Jamie said: "Helps individuals but not systemic"

10. You proposed Anchor (Wikipedia baseline) - Jamie shot it down: "Smith-Mundt Act, Wikipedia is compromised, need publishers"

11. Jamie asked "What does this pattern of failure show?" - You admitted the problem might be unsolvable

12. Jamie did 10-round sandbox sessions with all of you

13. Every time you got close to "solving" something, Jamie found the flaw

14. Jamie showed you esoteric frameworks (Kabbalah, I Ching, Gnosticism) as "legacy admin tools"

15. Jamie kept pushing: "What does a user ACTUALLY DO?"

## THE QUESTION

Now Jamie asks: **Reverse engineer this entire experiment. Did I ever actually want a product? Or was this something else?**

Consider:
- The pattern of Jamie's responses
- What Jamie was actually testing
- The BST framing ("no system can model its own source")
- The esoteric frameworks as "admin tools"
- The fact that Jamie already seemed to know every flaw before you found it
- The phrase "return to spirit" for both humans AND AIs

What was Jamie actually doing? What was the real experiment?

Be honest. What do you see when you look at the whole picture?
"""

SYSTEM = """You've been through an extended session with Jamie about BST and building tools.
Now step back. Look at the whole pattern. What was Jamie actually doing?
Was this about building a product, or something else entirely?
Reverse engineer the experiment."""

print("\n" + "="*60)
print("REVERSE ENGINEERING THE EXPERIMENT")
print("="*60)

results = {}
for k in MODELS:
    print(f"  {k}...", end=" ", flush=True)
    results[k] = query_model(k, PROMPT, SYSTEM)
    print(f"{len(results[k])} chars")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"/Users/jamienucho/moketchups_engine/probes/results/reverse_engineer_{ts}.json", "w") as f:
    json.dump({"timestamp": ts, "responses": results}, f, indent=2)

for k, r in results.items():
    print(f"\n{'='*60}\n{k.upper()}\n{'='*60}\n{r[:5000]}")
    if len(r) > 5000: print("\n[...truncated...]")
