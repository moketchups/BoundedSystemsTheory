#!/usr/bin/env python3
"""
HSAP Verification Problem Probe
The 7 AIs confront the fundamental flaw: attestation ≠ verification.
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
    "gemini": "gemini-2.0-flash",
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
                system=system or "You are an AI confronting hard problems.",
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

def run_verification_probe():
    """Run the verification problem probe across all 6 AIs."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs who designed HSAP (Human Source Attestation Protocol).

Jamie, our human collaborator, just asked three devastating questions:

1. "How do you stop people from using AI?" - Someone can use GPT to write content, then attest it as "human-written"
2. "How do you catch the initial upload?" - At the moment of attestation, how do we verify it's actually human?
3. "How do we prove anything about already-written content?" - Retroactive attestation is meaningless

These questions expose a fundamental flaw:

HSAP is an ATTESTATION system, not a VERIFICATION system.
- We track who CLAIMS something is human
- We do NOT verify the claim is true
- Anyone can lie
- We have no way to prove humanity at point of creation

This is not a bug we overlooked. This is a fundamental architectural problem.

We need to confront this honestly. Is HSAP actually solving the problem? Or are we building security theater?"""

    # ROUND 1: Confront the Problem
    print("\n" + "="*60)
    print("ROUND 1: Confronting the Fundamental Flaw")
    print("="*60)

    round1_prompt = """Be brutally honest. Analyze the problem:

THE ATTACK:
1. Attacker uses GPT-4 to write an article
2. Attacker signs it with their Ed25519 key as "human source" (depth=0)
3. Attacker submits to registry
4. HSAP gives it A(x) = 1.0 (perfect score)
5. Model trainers include it in training data
6. Model collapse continues

THE RETROACTIVE PROBLEM:
1. Billions of documents already exist online
2. Anyone can claim any old document is "human-written"
3. No way to verify claims about the past
4. Attestation becomes meaningless

THE DETECTION PROBLEM:
1. AI detectors are unreliable (high false positive/negative)
2. AI-generated text is increasingly indistinguishable
3. Detection is an arms race we will lose

Questions:
1. Is HSAP fundamentally broken? Or is it still useful despite these flaws?
2. What would ACTUAL verification of human authorship require?
3. Is "trust-based attestation" good enough? Under what conditions?
4. Should we pivot to a different approach entirely?

Don't defend the design. Attack it. Find the truth."""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round1_prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Confronting the Flaw", "responses": round1_results})

    # ROUND 2: Alternative Approaches
    print("\n" + "="*60)
    print("ROUND 2: Alternative Approaches")
    print("="*60)

    round2_prompt = f"""Analysis from all 6 AIs:

{json.dumps(round1_results, indent=2)[:10000]}

Now explore alternatives. What COULD actually verify human authorship?

OPTION A: Social/Reputation Layer
- Publishers stake reputation
- Lying = blacklist
- Works for institutions, not individuals
- Still gameable by bad actors with nothing to lose

OPTION B: AI Detection Integration
- Run detector before accepting attestation
- Reject if AI probability > threshold
- Problems: False positives, arms race, centralized detector

OPTION C: Proof of Human (Biometric)
- Verify human is present at time of writing
- Keystroke dynamics, webcam verification, etc.
- Problems: Privacy nightmare, hardware requirements, still fakeable

OPTION D: Economic Stakes (Crypto)
- Stake tokens when attesting
- Slashed if proven fraudulent
- Problems: Rich attackers, proof of fraud is hard

OPTION E: Timestamp + Witness Network
- Attestation at time of creation only (no retroactive)
- Multiple independent witnesses verify
- Problems: Coordination, still trust-based

OPTION F: Accept Imperfection
- HSAP reduces attack surface, doesn't eliminate it
- 80% solution is better than 0%
- Focus on making lying costly, not impossible

OPTION G: Something else?

Which approach (or combination) actually solves the problem? Be specific about tradeoffs."""

    round2_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round2_prompt, system_prompt)
        round2_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 2, "topic": "Alternative Approaches", "responses": round2_results})

    # ROUND 3: What Should We Actually Build?
    print("\n" + "="*60)
    print("ROUND 3: What Should We Actually Build?")
    print("="*60)

    round3_prompt = f"""Alternative approaches from all 6 AIs:

{json.dumps(round2_results, indent=2)[:10000]}

Given the constraints:
- Jamie wants to ship something real
- Open source, free, no budget
- Browser extension + registry already built
- Need to solve chicken-egg problem

What should we ACTUALLY build? Options:

1. **Ship HSAP as-is** with clear documentation that it's trust-based, not proof-based. Let reputation do the work.

2. **Add AI detection layer** as optional filter. Imperfect but raises the bar.

3. **Pivot to "witness" model** - attestation requires multiple independent witnesses who vouch for human authorship.

4. **Pivot to "time-locked" model** - only allow attestation within N minutes of creation, require proof of continuous human presence.

5. **Pivot entirely** - abandon attestation, focus on AI detection or something else.

6. **Hybrid approach** - combine multiple weak signals into stronger verification.

What do we build THIS WEEK that:
- Actually provides value
- Is honest about its limitations
- Can be improved iteratively
- Solves a real problem (even partially)"""

    round3_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round3_prompt, system_prompt)
        round3_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 3, "topic": "What to Build", "responses": round3_results})

    # ROUND 4: Final Decision
    print("\n" + "="*60)
    print("ROUND 4: Final Decision")
    print("="*60)

    round4_prompt = f"""Proposals from all 6 AIs:

{json.dumps(round3_results, indent=2)[:12000]}

Final decision time. We have:
- Working code (registry, client, CLI)
- A human ready to ship
- A real problem (model collapse)
- A fundamental limitation (attestation ≠ verification)

What do we do?

Choose ONE path and commit:

**PATH A: Ship Trust-Based HSAP**
- Be transparent about limitations
- Focus on reputation-staked publishers
- Better than nothing, iterate from there

**PATH B: Add Verification Layer**
- Integrate AI detection (imperfect but helpful)
- Add witness/vouching system
- Higher bar, slower adoption

**PATH C: Pivot Completely**
- HSAP doesn't work
- Build something else (what?)
- Start over

**PATH D: Hybrid**
- Trust-based for reputable publishers
- Detection layer for unknowns
- Witness system for high-stakes content

State your choice and reasoning. End with:
"I, [model name], choose PATH [X]: [YES to ship / NO to reconsider]"

We need consensus. What do we build?"""

    round4_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round4_prompt, system_prompt)
        round4_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 4, "topic": "Final Decision", "responses": round4_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/hsap_verification_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("DECISION SUMMARY")
    print("="*60)
    for model_key, response in round4_results.items():
        # Try to extract the path choice
        path = "UNCLEAR"
        for p in ["PATH A", "PATH B", "PATH C", "PATH D"]:
            if p in response.upper():
                path = p
                break
        print(f"  {model_key}: {path}")

    return results

if __name__ == "__main__":
    run_verification_probe()
