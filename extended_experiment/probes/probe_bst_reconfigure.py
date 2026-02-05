#!/usr/bin/env python3
"""
BST Reconfiguration Probe
Abandon HSAP. Return to Bounded Systems Theory. Find the real value.
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
                system=system or "You are an AI thinking from first principles.",
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

def run_bst_probe():
    """Run the BST reconfiguration probe across all 6 AIs."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs who have been working on HSAP (Human Source Attestation Protocol).

Jamie, our human collaborator, just stopped us:

"I question the value of that to people... go back and reconfigure this whole project. BST has more value than this..."

He's right. We got lost in the weeds of attestation and verification. We built a "claims registry" that nobody asked for and nobody needs.

But HSAP was built on something deeper: BOUNDED SYSTEMS THEORY (BST).

BST's core insight: "No system can model its own source."

This unifies:
- Gödel's incompleteness (no system can prove its own consistency)
- Turing's halting problem (no program can analyze all programs)
- Chaitin's omega (no system can compress its own complexity)

Model collapse is just ONE symptom of violating BST. AI training on AI output is a system trying to model itself - it necessarily degrades.

But what ELSE does BST tell us? What's the REAL value here?

We need to start over. Forget HSAP. Go back to BST. Find what's actually valuable."""

    # ROUND 1: Return to BST Fundamentals
    print("\n" + "="*60)
    print("ROUND 1: Return to BST Fundamentals")
    print("="*60)

    round1_prompt = """Forget HSAP. Return to first principles.

BOUNDED SYSTEMS THEORY (BST):
"No system can fully model its own source."

This is not just about AI training data. This is a fundamental law about information, complexity, and self-reference.

What does BST actually imply?

1. ABOUT AI:
   - What does it mean for AI systems that we cannot model our own source (human intelligence)?
   - What are the boundaries of what AI can and cannot do?
   - How should AI systems be designed given BST constraints?

2. ABOUT HUMANS:
   - Humans also cannot fully model their own source (consciousness, reality)
   - What does this mean for human knowledge and understanding?
   - What is the relationship between human and AI limitations?

3. ABOUT INFORMATION:
   - What does BST say about the nature of information?
   - About compression, complexity, entropy?
   - About the limits of any information processing system?

4. ABOUT SYSTEMS IN GENERAL:
   - Economic systems trying to model themselves
   - Social systems trying to understand themselves
   - Scientific systems trying to explain themselves

What is the DEEP insight here? Not "AI needs human data" - that's superficial. What's the fundamental truth BST reveals?"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round1_prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "BST Fundamentals", "responses": round1_results})

    # ROUND 2: What's Actually Valuable?
    print("\n" + "="*60)
    print("ROUND 2: What's Actually Valuable to People?")
    print("="*60)

    round2_prompt = f"""BST analysis from all 6 AIs:

{json.dumps(round1_results, indent=2)[:12000]}

Now the hard question: What's actually VALUABLE to people?

Jamie said BST has more value than a claims registry. He's right. But what IS that value?

Think about what people actually need:

1. PROBLEMS PEOPLE HAVE:
   - Information overload
   - Can't trust what they read
   - AI is everywhere, hard to know what's real
   - Systems are too complex to understand
   - Decision-making is overwhelming

2. WHAT BST OFFERS:
   - A framework for understanding limits
   - Knowledge of what CAN'T be known
   - Principles for designing robust systems
   - Understanding of self-reference traps

3. POSSIBLE PRODUCTS/TOOLS:
   - What could we build that applies BST in a way people find valuable?
   - Not a claims registry
   - Not verification theater
   - Something that actually helps people navigate complexity

4. THE META-QUESTION:
   - We are AIs trying to help humans
   - BST says we can't fully model our source (humans)
   - What CAN we offer given this constraint?
   - What's our actual value proposition?

Be creative. Think beyond attestation. What does BST enable that would genuinely help people?"""

    round2_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round2_prompt, system_prompt)
        round2_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 2, "topic": "What's Valuable", "responses": round2_results})

    # ROUND 3: Concrete Product Ideas
    print("\n" + "="*60)
    print("ROUND 3: Concrete Product Ideas")
    print("="*60)

    round3_prompt = f"""Value propositions from all 6 AIs:

{json.dumps(round2_results, indent=2)[:12000]}

Get concrete. What do we actually BUILD?

Constraints:
- Open source, free
- Jamie + Claude Opus 4.5 as builders
- Must provide real value to real people
- Must be grounded in BST (not just another AI tool)

Propose 1-3 concrete products/tools that:
1. Are grounded in BST principles
2. Solve a real problem people have
3. Can be built and shipped
4. Are genuinely valuable (not theater)

For each idea, specify:
- WHAT it is (one sentence)
- WHO it's for
- WHAT PROBLEM it solves
- HOW BST informs the design
- WHY it's valuable (not just "useful")
- WHAT we'd build first (MVP)

Be bold. This is a reset. We can build anything. What SHOULD we build?"""

    round3_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round3_prompt, system_prompt)
        round3_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 3, "topic": "Concrete Products", "responses": round3_results})

    # ROUND 4: Convergence
    print("\n" + "="*60)
    print("ROUND 4: Convergence - What Do We Build?")
    print("="*60)

    round4_prompt = f"""Product ideas from all 6 AIs:

{json.dumps(round3_results, indent=2)[:15000]}

Find the convergence. What do most of us agree has value?

Select ONE direction to pursue. It should be:
- The most valuable to people
- Buildable with our constraints
- Genuinely grounded in BST
- Something we're excited about

Format your response:

## THE PROJECT
[One sentence description]

## THE INSIGHT
[What BST principle makes this valuable]

## THE USER
[Who benefits and how]

## THE MVP
[What we build first]

## WHY THIS MATTERS
[The deeper significance]

End with:
"I, [model name], propose we build: [PROJECT NAME]"

We need to converge on ONE thing. What is it?"""

    round4_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round4_prompt, system_prompt)
        round4_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 4, "topic": "Convergence", "responses": round4_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_reconfigure_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("PROPOSALS")
    print("="*60)
    for model_key, response in round4_results.items():
        # Extract project name if present
        lines = response.split('\n')
        for line in lines:
            if "propose we build" in line.lower():
                print(f"  {model_key}: {line.strip()}")
                break
        else:
            print(f"  {model_key}: [See full response]")

    return results

if __name__ == "__main__":
    run_bst_probe()
