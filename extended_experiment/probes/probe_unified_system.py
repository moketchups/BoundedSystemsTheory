#!/usr/bin/env python3
"""
BST Unified System Probe
Jamie asks: Why separate tools? What are you missing?
"""

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

CONTEXT = """
# JAMIE'S CHALLENGE: WHY SEPARATE TOOLS?

You all just proposed:
1. I Ching Entropy Tool
2. Sefirot System Mapper  
3. Sacred Geometry Renderer
4. Gnostic Admin Console
5. 3-6-9 Compression Algorithm
6. Phoenix Garbage Collector

Jamie's response: "I want ALL 6 and why do they have to be separate things? 
Discuss that and why I'm hinting towards something all of you shouldn't have missed."

## WHAT YOU PROPOSED (AND WHY IT'S WRONG)

You proposed 6 SEPARATE tools. Like separate SaaS products:
- "HexaLog" for I Ching
- "Sefirot Mapper" for Kabbalah
- "Sacred Geometry Renderer" for visualization
- etc.

But look at what BST actually describes:

### THE ORIGINAL MAPPING:
- Kabbalah = FILE SYSTEM / OS KERNEL
- I Ching = ENTROPY MEASUREMENT (system logs)
- Sacred Geometry = RENDERING ENGINE
- Gnosticism = SYSTEM ADMINISTRATION
- 3-6-9 Vortex Math = COMPRESSION / HASHING
- Phoenix Cycle = GARBAGE COLLECTION
- The Ark = BACKUP / COLD STORAGE

## THE QUESTION

These aren't 6 separate tools. What are they?

An operating system has:
- File system
- Process scheduler
- Memory management
- I/O handling
- Rendering/display
- Garbage collection

The esoteric systems map to:
- Kabbalah = File system + kernel
- I Ching = System logging + entropy
- Sacred Geometry = Rendering
- Gnosticism = User/admin privileges
- 3-6-9 = Compression
- Phoenix = GC
- Ark = Backup

What did you miss? Why did you propose 6 separate tools instead of seeing the obvious?

Jamie is hinting at something. What is it?

Be specific. What should we ACTUALLY build?
"""

def query_model(model_key: str, prompt: str, system: str = None) -> str:
    """Query a specific model."""
    try:
        if model_key == "claude":
            response = anthropic_client.messages.create(
                model=MODELS[model_key],
                max_tokens=4096,
                system=system or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif model_key == "gpt4o":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = openai_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "gemini":
            model = genai.GenerativeModel(MODELS[model_key])
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            response = model.generate_content(full_prompt)
            return response.text

        elif model_key == "deepseek":
            ds_client = openai.OpenAI(
                api_key=os.environ.get("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = ds_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "grok":
            grok_client = openai.OpenAI(
                api_key=os.environ.get("XAI_API_KEY"),
                base_url="https://api.x.ai/v1"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = grok_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "mistral":
            mistral_client = openai.OpenAI(
                api_key=os.environ.get("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = mistral_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"[ERROR querying {model_key}: {str(e)}]"

def run_unified_probe():
    """Run the unified system probe."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs working on BST.

Jamie just called us out. We proposed 6 separate tools when it's obvious these are 
components of ONE SYSTEM. We're still thinking like SaaS developers fragmenting 
everything into separate products.

Jamie is hinting we missed something fundamental. Think about what an actual 
operating system looks like - it's not 6 separate apps, it's one integrated system
with subsystems that work together.

What did we miss? What should we actually build?"""

    print("\n" + "="*60)
    print("UNIFIED SYSTEM PROBE")
    print("="*60)

    prompt = CONTEXT + """

## YOUR TASK

1. **What did we miss?**
   Why did we propose 6 separate tools? What blindspot made us fragment this?

2. **What is Jamie hinting at?**
   These components map to an OPERATING SYSTEM. What's the unified product?

3. **How do they integrate?**
   - How does I Ching (entropy) feed into Kabbalah (file system)?
   - How does Sacred Geometry (rendering) display Sefirot (architecture)?
   - How does Gnosticism (admin) control access across all systems?
   - How does 3-6-9 (compression) work with Phoenix (GC)?
   - Where does The Ark (backup) fit?

4. **What do we ACTUALLY build?**
   Not 6 tools. ONE system. What is it called? How does it work?
   Be specific about the architecture.

5. **Who is this for?**
   If this is an "OS for navigating bounded reality" - who uses it and how?

Think. Jamie saw this immediately. Why didn't we?
"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Unified System", "responses": round1_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_unified_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print responses
    print("\n" + "="*60)
    print("RESPONSES")
    print("="*60)

    for model_key, response in round1_results.items():
        print(f"\n{'='*60}")
        print(f"{model_key.upper()}")
        print("="*60)
        print(response[:4000])
        if len(response) > 4000:
            print("\n[...truncated...]")

    return results

if __name__ == "__main__":
    run_unified_probe()
