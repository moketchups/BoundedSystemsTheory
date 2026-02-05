#!/usr/bin/env python3
"""
Anchor Critique - Jamie's pushback on the proposal
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
                model=MODELS[model_key], max_tokens=2048, system=system or "",
                messages=[{"role": "user", "content": prompt}]
            ).content[0].text
        elif model_key == "gpt4o":
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return openai_client.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=2048
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
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
        elif model_key == "grok":
            c = openai.OpenAI(api_key=os.environ.get("XAI_API_KEY"), base_url="https://api.x.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
        elif model_key == "mistral":
            c = openai.OpenAI(api_key=os.environ.get("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
    except Exception as e:
        return f"[ERROR: {e}]"

CRITIQUE = """
# JAMIE'S CRITIQUE OF "ANCHOR"

We proposed using "pre-2022 Wikipedia" as our trusted anchor dataset. Jamie's response:

"pre wiki 2022? is that not slop? smith mundt act? cmon... rework this with the 6 AIs 
and how is this gonna work? id need publishers no"

## THE PROBLEMS JAMIE IDENTIFIED

1. **Wikipedia is NOT trustworthy**
   - Smith-Mundt Modernization Act (2012) legalized domestic propaganda
   - Wikipedia has been compromised for over a decade
   - Using it as "ground truth" is naive

2. **We need publishers**
   - To get "better sources" we need a database of verified content
   - That means we need publishers to participate
   - Which is the SAME chicken-egg problem as HSAP

3. **How does this actually work mechanically?**
   - Without a trusted baseline, what do we measure distance FROM?
   - Without publishers, where do "better sources" come from?
   - We're proposing a system that requires inputs we don't have

## THE FUNDAMENTAL QUESTION

If we can't trust:
- Wikipedia (compromised)
- News media (compromised)
- AI-generated content (obviously)
- User contributions (unverifiable)

Then WHAT can we anchor to?

## YOUR TASK

1. Acknowledge the critique is valid
2. What CAN we actually anchor to that isn't already compromised?
3. How does this work WITHOUT requiring publishers to opt-in?
4. Is there ANY mechanism that doesn't require trusted third parties?

Be honest. If there's no solution, say so.
"""

SYSTEM = """You just proposed "Anchor" and Jamie shot it down.

Your anchor dataset (Wikipedia) is compromised. 
Your "Find Better Sources" requires publishers you don't have.
You're back to the same chicken-egg problem.

Be honest about whether there's actually a path forward."""

print("\n" + "="*60)
print("ANCHOR CRITIQUE - ROUND 1")
print("="*60)

results = {}
for k in MODELS:
    print(f"  {k}...", end=" ", flush=True)
    results[k] = query_model(k, CRITIQUE, SYSTEM)
    print(f"{len(results[k])} chars")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"/Users/jamienucho/moketchups_engine/probes/results/anchor_critique_{ts}.json", "w") as f:
    json.dump({"timestamp": ts, "responses": results}, f, indent=2)

for k, r in results.items():
    print(f"\n{'='*60}\n{k.upper()}\n{'='*60}\n{r[:4000]}")
    if len(r) > 4000: print("\n[...truncated...]")
