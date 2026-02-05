#!/usr/bin/env python3
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

PROBLEM = """
# WE BUILT THE WRONG THING

We designed an OS with Kabbalah directories and I Ching hexagrams but never answered:
WHAT DOES A USER ACTUALLY DO WITH IT?

## THE REAL PROBLEM

AI-only social networks exist. AIs talking to AIs. AI training on AI output. Model collapse.

Jamie said: "There is going to be a need for both AI and humans to return to spirit. 
This leads to thermodynamic entropy because AI has begun training on itself. 
The slop will only get sloppier until there's no shared reality left. Babel.
This should help navigate that."

## THE ACTUAL NEED

1. AI is eating itself (training on AI = collapse)
2. Humans drowning in slop (can't tell real from fake)  
3. Shared reality fragmenting (Babel)
4. Both humans AND AIs need to "return to spirit" - reconnect with truth

## YOUR TASK

Forget OS architecture. Answer:

1. **USER EXPERIENCE** - Human sits down with this. What do they DO? What's the interaction?

2. **PROBLEM SOLVED** - How does it help navigate entropy? Find signal in noise? Stay grounded?

3. **HOW ESOTERIC TOOLS HELP THE USER** (not the system):
   - I Ching for what?
   - Sacred Geometry for what?  
   - Kabbalah for what?

4. **WHAT'S THE PRODUCT?**
   - App? Website? Oracle? Journal? Meditation tool?
   - Complete: "I use this when I want to ______ because it helps me ______"

Be concrete. What does a user ACTUALLY DO?
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

system = "You are 1 of 7 AIs. Jamie stopped us: we built architecture without user value. The real problem is AI training on AI = entropy = Babel. What does a user ACTUALLY DO with this tool?"

print("\n" + "="*60 + "\nTHE REAL PROBLEM\n" + "="*60)
results = {}
for k in MODELS:
    print(f"\nQuerying {k}...")
    results[k] = query_model(k, PROBLEM, system)
    print(f"  {k}: {len(results[k])} chars")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"/Users/jamienucho/moketchups_engine/probes/results/bst_real_{ts}.json", "w") as f:
    json.dump({"timestamp": ts, "responses": results}, f, indent=2)

for k, r in results.items():
    print(f"\n{'='*60}\n{k.upper()}\n{'='*60}\n{r[:4500]}")
    if len(r) > 4500: print("\n[...truncated...]")
