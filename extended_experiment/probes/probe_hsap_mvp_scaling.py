#!/usr/bin/env python3
"""
HSAP MVP Scaling Probe
Takes scaling concerns to the 6 AIs to design a deployable MVP.

Current state: Proof of concept on single machine (SQLite)
Goal: MVP that works across the internet
"""

import anthropic
import openai
import google.generativeai as genai
import os
import json
from datetime import datetime

# Initialize clients
anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

MODELS = {
    "gpt4o": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash-exp",
    "deepseek": "deepseek-chat",
    "grok": "grok-3-latest",
    "mistral": "mistral-large-latest",
}

def query_model(model_key: str, prompt: str, system: str = None) -> str:
    """Query a specific model."""
    try:
        if model_key == "claude":
            response = anthropic_client.messages.create(
                model=MODELS[model_key],
                max_tokens=4096,
                system=system or "You are an AI architect designing scalable systems.",
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

def run_scaling_probe():
    """Run the MVP scaling probe across all 6 AIs."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs who designed HSAP (Human Source Attestation Protocol) to prevent AI model collapse.

HSAP works by:
1. Cryptographically attesting human-originated data (Ed25519 signatures)
2. Tracking derivation depth d(x) through a provenance DAG
3. Computing attestation scores A(x) = γ^d(x) that decay with distance from human source
4. Filtering training data to exclude items where A(x) < τ (default 0.5)

We built a working proof of concept (Python, SQLite, local machine). Now we need to scale it to an MVP that works across the internet.

Your task: Design practical solutions that can be implemented quickly. No blockchain unless absolutely necessary. Prefer federation, existing infrastructure, and pragmatic tradeoffs."""

    # ROUND 1: Problem Analysis
    print("\n" + "="*60)
    print("ROUND 1: Scaling Problem Analysis")
    print("="*60)

    round1_prompt = """The HSAP proof of concept has these scaling limitations:

1. **Storage**: SQLite on single machine. Can't share attestations across organizations.

2. **Identity**: Who can create root attestations? How do we prevent fake "human" attestations from bots?

3. **Discovery**: How does a model trainer find attestations for data they scraped? Attestations are separate from content.

4. **Adoption**: Chicken-egg problem. No one attests if no one filters. No one filters if nothing is attested.

5. **Cross-org trust**: Why should OpenAI trust attestations from random publishers?

Analyze these problems. Which is the most critical to solve first for an MVP? What's the minimum viable solution for each?

Be specific and practical. We want to deploy something within weeks, not years."""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round1_prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Problem Analysis", "responses": round1_results})

    # ROUND 2: Architecture Proposals
    print("\n" + "="*60)
    print("ROUND 2: MVP Architecture Proposals")
    print("="*60)

    round2_prompt = f"""Based on the problem analysis from all 6 AIs:

{json.dumps(round1_results, indent=2)[:8000]}

Now propose a concrete MVP architecture. Consider these options:

**Option A: Federated Servers**
- Multiple attestation servers (like email: anyone can run one)
- Shared protocol, independent databases
- Cross-server verification via signed attestations

**Option B: Content-Embedded**
- Embed attestation signatures directly in content (metadata, watermarks, steganography)
- No central lookup needed - attestation travels with content
- Verification is local

**Option C: DNS-style Registry**
- Central registry mapping content hashes to attestation records
- Like DNS: hierarchical, cacheable, federated
- Single lookup protocol, distributed infrastructure

**Option D: Something else?**

Propose ONE architecture for the MVP. Specify:
1. How attestations are stored and discovered
2. How identity/trust is bootstrapped
3. What existing infrastructure it leverages
4. What can be built in 2-4 weeks
5. Migration path from proof of concept"""

    round2_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round2_prompt, system_prompt)
        round2_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 2, "topic": "Architecture Proposals", "responses": round2_results})

    # ROUND 3: Convergence
    print("\n" + "="*60)
    print("ROUND 3: Convergence on MVP Spec")
    print("="*60)

    round3_prompt = f"""Architecture proposals from all 6 AIs:

{json.dumps(round2_results, indent=2)[:12000]}

Find the convergence. What do most AIs agree on? Where are the key disagreements?

Produce a FINAL MVP SPECIFICATION that:
1. Can be built by a small team in 2-4 weeks
2. Solves the minimum necessary scaling problems
3. Provides a clear adoption path
4. Is backwards compatible with our proof of concept

Format your response as:

## MVP SPEC: HSAP v1.1

### Architecture Decision
[Which option and why]

### Components to Build
[Concrete list with effort estimates]

### Identity Bootstrap
[How trust is established]

### Discovery Mechanism
[How attestations are found]

### Adoption Strategy
[First users, forcing functions]

### What We're NOT Doing (Yet)
[Explicit scope cuts for v1.1]"""

    round3_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round3_prompt, system_prompt)
        round3_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 3, "topic": "MVP Specification", "responses": round3_results})

    # ROUND 4: Final Consensus
    print("\n" + "="*60)
    print("ROUND 4: Final Consensus Vote")
    print("="*60)

    round4_prompt = f"""MVP specifications from all 6 AIs:

{json.dumps(round3_results, indent=2)[:15000]}

This is the final round. We need ONE specification all 7 AIs (including the builder, Claude Opus 4.5) can implement.

Review all proposals and produce a FINAL CONSENSUS document:

1. State the core architecture decision (1 sentence)
2. List exactly what needs to be built (numbered list)
3. Specify the tech stack
4. Define the API surface
5. Describe the deployment model
6. Give the adoption playbook (first 3 steps)

End with: "I, [model name], agree to this specification: [YES/NO]"

If NO, state your blocking concern."""

    round4_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round4_prompt, system_prompt)
        round4_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 4, "topic": "Final Consensus", "responses": round4_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/hsap_mvp_scaling_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("CONSENSUS SUMMARY")
    print("="*60)
    for model_key, response in round4_results.items():
        vote = "YES" if "YES" in response.upper() and "I," in response else "UNCLEAR"
        print(f"  {model_key}: {vote}")

    return results

if __name__ == "__main__":
    run_scaling_probe()
