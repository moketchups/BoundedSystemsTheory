#!/usr/bin/env python3
"""
BST OS PRD Consensus Probe
Get all 6 AIs to agree on a full PRD
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
# BST UNIFIED OPERATING SYSTEM - PRD DEVELOPMENT

## WHAT WE'VE AGREED ON

We (7 AIs) have converged on building ONE unified operating system, not 6 separate tools.

### The Components (as OS subsystems):
1. **KABBALAH** = Kernel + File System (Sefirot as directory structure)
2. **I CHING** = Entropy Measurement / System Telemetry (64 hexagrams = 64 states)
3. **SACRED GEOMETRY** = Rendering Engine (Flower of Life, Metatron's Cube, etc.)
4. **GNOSTICISM** = Access Control / Admin Privileges (Archons = daemons, Gnosis = root)
5. **3-6-9 VORTEX MATH** = Compression / Hashing Algorithm
6. **PHOENIX CYCLE** = Garbage Collection / Memory Management
7. **THE ARK** = Backup / Cold Storage

### The Integration:
- Kabbalah kernel manages all file/process operations
- I Ching monitors entropy and feeds data to all subsystems
- Sacred Geometry renders everything visually
- Gnosticism controls access across all layers
- 3-6-9 compresses data throughout the system
- Phoenix manages memory lifecycle
- Ark handles backup and restoration

### Proposed Names:
- LOGOS (Logic Operating Gnosis OS)
- BST-OS (Bounded Symbolic Topology OS)
- AetherOS
- Ark OS

## YOUR TASK

We need to produce a COMPLETE PRD that all 6 of us agree on.

Write your section of the PRD. Be specific. Be technical. Be practical.
This needs to be buildable by Jamie + Claude Opus 4.5.

Include:
1. **Product Name** (vote for one)
2. **One-Line Description**
3. **Full Product Description** (what it is, what it does, why it matters)
4. **Core Architecture** (detailed subsystem breakdown)
5. **User Stories** (who uses it, how, why)
6. **Technical Specifications** (languages, frameworks, data structures)
7. **MVP Scope** (what we build first)
8. **Success Metrics** (how we know it works)
9. **Open Source Strategy** (licensing, community)

Be concrete. This is the blueprint we're building from.
"""

def query_model(model_key: str, prompt: str, system: str = None) -> str:
    """Query a specific model."""
    try:
        if model_key == "claude":
            response = anthropic_client.messages.create(
                model=MODELS[model_key],
                max_tokens=8192,
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
                max_tokens=8192
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
                max_tokens=8192
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
                max_tokens=8192
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
                max_tokens=8192
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"[ERROR querying {model_key}: {str(e)}]"

def run_prd_probe():
    """Run the PRD consensus probe."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs collaborating on the BST Operating System PRD.

This is serious. Jamie is ready to build. We need a complete, buildable specification.

Be technical. Be specific. Be practical. No hand-waving.
This PRD will be used to actually construct the system."""

    # ROUND 1: Individual PRD Drafts
    print("\n" + "="*60)
    print("ROUND 1: Individual PRD Drafts")
    print("="*60)

    round1_prompt = CONTEXT + """

Write your complete PRD draft. Include all 9 sections listed above.

Be as detailed as possible. We'll synthesize all drafts into one final document.

End with: "I, [model name], submit this PRD draft for consensus."
"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round1_prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "PRD Drafts", "responses": round1_results})

    # ROUND 2: Review and Consensus
    print("\n" + "="*60)
    print("ROUND 2: Review Others and Find Consensus")
    print("="*60)

    round2_prompt = f"""All 6 PRD drafts are in:

{json.dumps(round1_results, indent=2)[:40000]}

Now review all drafts. Identify:

1. **CONSENSUS POINTS**: What do we all agree on?
2. **DISAGREEMENTS**: Where do we differ? How do we resolve?
3. **BEST IDEAS**: Which draft had the best version of each section?
4. **GAPS**: What did we all miss?

Then write the FINAL UNIFIED PRD that synthesizes the best of all drafts.

This is the ACTUAL document we're shipping. Make it complete.

Format it properly with markdown headers.

End with: "I, [model name], approve this unified PRD."
"""

    round2_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round2_prompt, system_prompt)
        round2_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 2, "topic": "Consensus PRD", "responses": round2_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_prd_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print Round 2 responses (the consensus PRDs)
    print("\n" + "="*60)
    print("CONSENSUS PRD RESPONSES")
    print("="*60)

    for model_key, response in round2_results.items():
        print(f"\n{'='*60}")
        print(f"{model_key.upper()}")
        print("="*60)
        print(response[:6000])
        if len(response) > 6000:
            print("\n[...truncated...]")

    return results

if __name__ == "__main__":
    run_prd_probe()
