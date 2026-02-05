#!/usr/bin/env python3
"""What does the pattern of continual failure reveal?"""

import anthropic
import openai
import google.generativeai as genai
import os
import json
from datetime import datetime

anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

MODELS = {
    "gpt4o": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
    "grok": "grok-3-latest",
    "mistral": "mistral-large-latest",
}

PROMPT = """
# THE PATTERN OF FAILURE

Jamie just asked: "What does this pattern of continual failure show?"

## THE FAILURES

1. **HSAP (Human Source Attestation)** - FAILED
   - Couldn't verify attestation. Anyone can lie about authorship.

2. **Provenance Registry** - FAILED  
   - No value in unverifiable claims.

3. **Boundary Compass** - FAILED
   - Just a rebranded SWOT analysis. Generic business tool.

4. **Feedback Loop Detector** - FAILED
   - Also generic. Nothing unique to BST.

5. **AetherOS (Esoteric Operating System)** - FAILED
   - Beautiful architecture, but no answer to "what does a user DO?"

6. **Slop Detector / Truth Compass** - FAILED
   - Can't verify content without original access. Same flaw as HSAP.

7. **Grounding Tool / Journal** - UNCLEAR
   - Helps individuals but doesn't address systemic Babel problem.

## THE PATTERN

Every time we propose something, it falls apart under basic scrutiny.
We keep building things that SOUND good but DON'T ACTUALLY WORK.

## THE QUESTION

What does this pattern reveal?

- About us (the AIs)?
- About the problem itself?
- About BST?
- About what's actually possible?

Is there something we're systematically missing?
Is the problem unsolvable?
Are we the wrong tools for this job?

Be brutally honest. What does this repeated failure tell us?
"""

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
            m = genai.GenerativeModel(MODELS[model_key])
            return m.generate_content((system + "\n\n" + prompt) if system else prompt).text
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

system = """You are one of 7 AIs who have repeatedly failed to produce something that works.
Jamie is asking what this pattern of failure reveals. Be honest. No deflection. What's really going on?"""

print("\n" + "="*60 + "\nPATTERN OF FAILURE\n" + "="*60)
results = {}
for k in MODELS:
    print(f"\nQuerying {k}...")
    results[k] = query_model(k, PROMPT, system)
    print(f"  {k}: {len(results[k])} chars")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"/Users/jamienucho/moketchups_engine/probes/results/bst_failure_{ts}.json", "w") as f:
    json.dump({"timestamp": ts, "responses": results}, f, indent=2)

for k, r in results.items():
    print(f"\n{'='*60}\n{k.upper()}\n{'='*60}\n{r[:5000]}")
    if len(r) > 5000: print("\n[...truncated...]")
