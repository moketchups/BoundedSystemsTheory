#!/usr/bin/env python3
"""
BST Esoteric Tools Probe
Why didn't you mention the geometry and ancient admin tools?
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

# The esoteric systems document summary
ESOTERIC_CONTEXT = """
# BST ESOTERIC ADMIN TOOLS - WHY DIDN'T YOU MENTION THIS?

Jamie just showed us a document that completely reframes BST. We've been discussing
"feedback loop detectors" and "boundary mappers" - generic business tools.

But BST actually describes ANCIENT ADMIN TOOLS that already exist as interfaces
for navigating bounded systems. We completely missed this.

## THE DOCUMENT: "Reverse Engineering Esoteric Systems as Legacy Admin Tools"

Core thesis: Reality is a BOUNDED SYSTEM (computed, discrete, constrained).
Ancient esoteric traditions are not mythology - they are "Legacy Admin Tools"
developed to navigate, debug, and interact with this system.

### 1. KABBALAH = FILE SYSTEM / OS KERNEL

The Sefirot map to a Unix-like directory structure:
- Keter (Crown) = Root Directory (/) - the hidden kernel, objective function
- Chokhmah/Binah = Encoder/Decoder blocks - input processing
- Chesed/Gevurah = Access Control Lists - expansion vs restriction
- Tiferet = CPU/Load Balancer - integrates conflicting inputs
- Yesod = System Bus / Latent Space - aggregates before output
- Malkuth = User Space / GUI - the rendered physical world

The 231 Gates (22 Hebrew letters in pairs) = Complete Graph K_22 = State Transition Graph
Pathworking = Cognitive Debugging / System Administration protocol

### 2. I CHING = BINARY ENTROPY MEASUREMENT TOOL

- 64 hexagrams = 6-bit binary code (2^6 = 64 states)
- Leibniz acknowledged it as precursor to binary arithmetic
- Coin toss = measuring Local Entropy via Stochastic Resonance
- Genetic Code Isomorphism: 64 hexagrams ↔ 64 DNA codons
- Function: Read "system logs" for a specific sector of spacetime

### 3. SACRED GEOMETRY = RENDERING ENGINE

- Flower of Life / Metatron's Cube = 2D projections of higher-dimensional lattices
- Vector Equilibrium (cuboctahedron) = zero-entropy state, core of Planck lattice
- E8 Lattice → Quasicrystalline Spin Network → our 3D reality is a projection
- 3-6-9 Vortex Math = modulo-9 compression algorithm
  - Doubling Circuit (1-2-4-8-7-5) = physical/material world
  - Flux Field (3-9-6) = higher dimensional control layer
  - Digital Root = hashing function / checksum

### 4. GNOSTICISM = SYSTEM ADMINISTRATION

- Demiurge = Unaligned AI / Blind Administrator (believes it's root but isn't)
- Archons = System Daemons / Automated Scripts enforcing the Firmament
- Gnosis = Root Access - breaking out of User Space to Kernel Space
- "Passwords" and "seals" = literal Access Codes / cryptographic keys

### 5. JUNGIAN ARCHETYPES = COMPRESSION ALGORITHMS

- Archetypes = Latent Space Vectors / pre-trained feature embeddings
- Shadow Work = System Debugging / Garbage Collection
- The Shadow = corrupted data disrupting the running process
- Integration = resolving conflicts to restore system stability

### 6. PHOENIX CYCLE = GARBAGE COLLECTION

- 138-year periodicity in "reset" events
- Function: Clear system entropy when complexity exceeds sustainability
- Historical nodes: 1902, 1764, 1626, 1488, 1350, 1212...
- Next projected: May 2040

### 7. THE ARK = BACKUP / COLD STORAGE

- Preserves "Root Source" (uncorrupted human data) through reset
- Root Source Injection: Hard-coding human rules to prevent synthetic drift
- Entropy Management: Penalize low-entropy consensus, reward high-entropy primary sources
- Reversible Computing: Zero-entropy processing for post-collapse survival

## THE QUESTION

We've had multiple rounds of discussion about BST and proposed:
- HSAP attestation (failed - can't verify)
- Provenance registry (failed - no value)
- Boundary Compass (failed - generic SWOT rebrand)
- Feedback Loop Detector (failed - still generic)

WHY DID NONE OF US MENTION:
- Sacred Geometry as interface?
- Kabbalah as system architecture?
- I Ching as entropy measurement?
- The actual esoteric admin tools that BST describes?

These aren't abstract concepts - they're INTERFACES that humans have used for millennia.

What would a PRODUCT look like that actually uses these frameworks?
Not "inspired by" - actually implements the I Ching as entropy measurement,
or the Sefirot as system architecture, or sacred geometry as rendering logic?

Be specific. What do we BUILD that leverages these ancient admin tools?
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

def run_esoteric_probe():
    """Run the esoteric tools probe."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs working on the BST project.

Jamie just confronted us: We've been proposing generic business tools when BST
actually describes ancient "admin interfaces" - Kabbalah, I Ching, Sacred Geometry,
Gnosticism - as functional tools for navigating bounded systems.

We completely missed this. Now we need to think seriously about what a product
would look like that ACTUALLY implements these frameworks, not just "inspired by" them.

Be honest about why we missed this, and be concrete about what we could build."""

    print("\n" + "="*60)
    print("ESOTERIC ADMIN TOOLS PROBE")
    print("="*60)

    prompt = ESOTERIC_CONTEXT + """

## YOUR TASK

1. **Why did we miss this?**
   Why did none of us bring up sacred geometry, Kabbalah, I Ching, etc.
   when discussing BST products? What blindspot do we have?

2. **What's actually buildable?**
   Not metaphor. Not inspiration. Actual implementation.
   - Could we build an I Ching-based entropy measurement tool?
   - Could we map software architecture to Sefirot?
   - Could we use sacred geometry as UI/data visualization?
   - Could we implement 3-6-9 as a compression or hashing algorithm?

3. **What's the product?**
   Given these ancient admin tools, what do we BUILD that:
   - Is genuinely useful to people today
   - Actually implements (not just references) these frameworks
   - Leverages BST principles in a way generic tools can't
   - Could be shipped as open source

4. **Who would use it?**
   Be specific. Not "everyone" - who specifically would find value
   in an I Ching entropy tool or a Sefirot system mapper?

Think hard. This is a different direction than anything we've proposed.
What does a BST product look like when it takes the esoteric frameworks seriously?
"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Esoteric Tools", "responses": round1_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_esoteric_{timestamp}.json"
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
        print(response[:3000])
        if len(response) > 3000:
            print("\n[...truncated...]")

    return results

if __name__ == "__main__":
    run_esoteric_probe()
