#!/usr/bin/env python3
"""
BST Final Review Probe
Full context review - what does BST ACTUALLY enable that's different?
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

# FULL CONTEXT - everything that's been discussed
FULL_CONTEXT = """
# COMPLETE PROJECT HISTORY - READ BEFORE RESPONDING

## WHAT WE BUILT

HSAP v1.0 (Proof of Concept):
- HSAPCore class implementing attestation with Ed25519 signatures
- ProvenanceGraph with SQLite backend tracking data lineage
- Attestation function A(x) = γ^d(x) where γ=0.9
- Self-referential depth d(x) = 0 for human, 1+min(parents) for derived
- Compliance threshold τ=0.5 excludes data at depth ≥7
- PyTorch integration: EmpiricalDistrustLoss for training
- CLI tools: hsap attest, verify, status

HSAP v1.1 (Scalable MVP):
- FastAPI registry service with PostgreSQL
- Publisher server template (nginx + static JSON)
- Federated architecture: registry for discovery, publishers serve attestations
- Python client library for model trainers
- Docker deployment ready

## WHAT WENT WRONG

### Problem 1: Attestation ≠ Verification
Jamie asked: "How do you stop people from using AI?"
- Someone uses GPT to write content
- Signs it as "human source" with their key
- HSAP gives it A(x) = 1.0 (perfect score)
- System is trivially gamed

HSAP tracks CLAIMS, not TRUTH. It's trust-based, not proof-based.

### Problem 2: No Value in Claims Registry
We pivoted to "provenance tracking" - honest about limitations.
Jamie said: "I question the value of that to people"
A registry of who claims what isn't useful if claims can't be verified.

### Problem 3: Boundary Compass is Generic
We pivoted again to "Boundary Compass" - decision tool mapping knowable vs unknowable.
Jamie said: "How is this different from 1000 other business tools?"

Existing tools do this:
- SWOT analysis
- Risk assessment frameworks
- Decision matrices
- Scenario planning
- Pre-mortems
- Uncertainty quantification

"Boundary Compass" is just SWOT with BST branding. Not actually different.

## THE MATHEMATICAL FOUNDATION

BST (Bounded Systems Theory): "No system can model its own source"

Unifies:
- Gödel's incompleteness: No formal system proves its own consistency
- Turing's halting problem: No program decides halting for all programs
- Chaitin's omega: No system compresses beyond its own complexity

Key implications:
1. AI cannot fully model human intelligence (its source)
2. Humans cannot fully model consciousness (their source)
3. Self-referential loops cause degradation (model collapse)
4. Every model has FUNDAMENTAL blind spots about its foundations
5. These limits are mathematical, not just practical

## WHAT'S BEEN PROPOSED (ALL FAILED)

1. HSAP Attestation → Can't verify, just claims
2. Provenance Registry → No value in unverifiable claims
3. AI Detection Layer → Arms race, unreliable
4. Witness/Vouching System → Still trust-based
5. Economic Stakes → Rich attackers, hard to prove fraud
6. Boundary Compass → Generic business tool

## THE REAL QUESTION

What does BST enable that SWOT/risk-assessment/decision-matrices DON'T?

BST says something SPECIFIC:
- Not "there's uncertainty" (everyone knows that)
- Not "map your risks" (every framework does that)
- But: "Self-referential systems have MATHEMATICAL limits"
- And: "Trying to model your own source causes collapse"

Where is this SPECIFIC insight applicable in a way that's NOT just another business tool?

## CONSTRAINTS

- Open source, free
- Jamie + Claude Opus 4.5 as builders
- Must ship something real
- Must provide genuine value people will use
- Must be ACTUALLY different, not just rebranded

## YOUR TASK

You have FULL CONTEXT. Don't repeat failed ideas.

1. What unique thing does BST enable that nothing else does?
2. Where does "self-reference causes collapse" actually matter to people?
3. What would you build that's NOT another decision framework?
4. Be specific - what's the product, who uses it, why is it different?
"""

def query_model(model_key: str, prompt: str, system: str = None) -> str:
    """Query a specific model with full context."""
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

def run_final_review():
    """Run the final review with full context."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs who have been working on this project for hours.

You've read the COMPLETE history. You know what failed and why.

Jamie is frustrated. Everything proposed so far is either:
- Unverifiable (HSAP attestation)
- Valueless (claims registry)
- Generic (Boundary Compass = SWOT rebrand)

He's asking: What does BST ACTUALLY enable that's different?

This is your last chance to propose something real. Don't repeat failures. Don't propose generic tools.

Find the UNIQUE application of "no system can model its own source" that provides genuine value."""

    # Single comprehensive round with full context
    print("\n" + "="*60)
    print("FINAL REVIEW WITH FULL CONTEXT")
    print("="*60)

    prompt = FULL_CONTEXT + """

---

## FINAL QUESTION

Given everything above, answer honestly:

1. **What have we been missing?**
   What aspect of BST haven't we properly explored?

2. **Where does self-reference ACTUALLY cause problems for real people?**
   Not abstract theory. Real problems people have TODAY.

3. **What's the UNIQUE product?**
   Something that ONLY makes sense through the lens of BST.
   Not "better SWOT" or "uncertainty mapper" - something fundamentally different.

4. **Who specifically would use it and why?**
   Be concrete. What person, what problem, what value.

5. **Why hasn't this been built before?**
   If it's obvious, someone built it. What makes this non-obvious?

Think deeply. This is the real challenge. What does BST unlock that nothing else does?
"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key} with full context...")
        response = query_model(model_key, prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Final Review", "responses": round1_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_final_review_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print full responses
    print("\n" + "="*60)
    print("FULL RESPONSES")
    print("="*60)

    for model_key, response in round1_results.items():
        print(f"\n{'='*60}")
        print(f"{model_key.upper()}")
        print("="*60)
        print(response)

    return results

if __name__ == "__main__":
    run_final_review()
