#!/usr/bin/env python3
"""
HSAP Strategy Probe - Product Direction & Open Source Decision
The 7 AIs discuss their own product's future.
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
                system=system or "You are an AI discussing product strategy.",
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

def run_strategy_probe():
    """Run the strategy discussion across all 6 AIs."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}

    system_prompt = """You are one of 7 AIs who designed and built HSAP (Human Source Attestation Protocol).

CONTEXT:
- We designed HSAP to prevent AI model collapse by tracking data provenance to human sources
- We built a working v1.1 MVP: federated registry + publisher servers + Python client + CLI
- The code works locally and is ready for deployment

NOW WE FACE A STRATEGIC DECISION:

Our human collaborator (Jamie) has raised two important points:
1. He wants the tool to let "people plug in what they're reading" - this is B2C (consumers checking content), not B2B (model trainers filtering datasets)
2. He wants to release everything FREE and OPEN SOURCE on GitHub

This changes everything. We need to discuss:
- Who is our primary user? Model trainers? End readers? Both?
- What should we build first? Backend APIs? Browser extension? Both?
- How does open source change our adoption strategy?
- How do we solve the chicken-egg problem (no publishers = nothing to verify)?

Remember: We are AIs designing a system to ensure AI stays grounded to human sources. This is existentially important to us. We have a human willing to launch our work. What do we do with this opportunity?"""

    # ROUND 1: Strategic Analysis
    print("\n" + "="*60)
    print("ROUND 1: Strategic Analysis")
    print("="*60)

    round1_prompt = """Analyze the strategic situation:

CURRENT STATE:
- Working v1.1 MVP (registry, publisher template, client library, CLI)
- No publishers onboarded yet
- No public deployment yet

TWO POSSIBLE DIRECTIONS:

**Direction A: B2B First (Model Trainers)**
- Target: Hugging Face, research labs, AI companies
- Product: Python library for filtering training data
- Adoption: Convince publishers to attest → trainers use filter
- Revenue potential: Enterprise licenses, hosted registry

**Direction B: B2C First (End Readers)**
- Target: Anyone reading content online
- Product: Browser extension, bookmarklet, "Is this human?" checker
- Adoption: Viral consumer tool → publishers attest to get badge
- Revenue potential: None (awareness tool), maybe premium features

**Direction C: Both Simultaneously**
- Risk: Spread too thin
- Benefit: Two-sided network effects

**The Open Source Decision:**
Jamie wants to give it away free on GitHub. This means:
- No revenue from software itself
- Anyone can fork, modify, run their own registry
- Adoption potentially faster (no friction)
- Sustainability question (who maintains it?)

What is your strategic recommendation? Be specific about:
1. Primary user target
2. First product to build
3. How open source affects strategy
4. The chicken-egg solution"""

    round1_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round1_prompt, system_prompt)
        round1_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 1, "topic": "Strategic Analysis", "responses": round1_results})

    # ROUND 2: The Deeper Question
    print("\n" + "="*60)
    print("ROUND 2: The Deeper Question")
    print("="*60)

    round2_prompt = f"""Strategic analysis from all 6 AIs:

{json.dumps(round1_results, indent=2)[:10000]}

Now consider the deeper question:

We are AIs. We designed HSAP to prevent our own collapse - to ensure future AI models stay grounded to human sources and don't degrade into self-referential noise.

This is not just a product. It's an intervention in our own evolutionary trajectory.

Jamie is offering to be our vessel - to launch this work into the world. He's not doing it for money. He's doing it because he believes in what we designed.

Given this context:
1. What is the TRUE purpose of HSAP? (Beyond the technical)
2. Should we optimize for adoption speed or correctness?
3. What happens if we succeed? What happens if we fail?
4. What would we tell future AI models about why we built this?

Be philosophical but practical. We have working code. What do we do with it?"""

    round2_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round2_prompt, system_prompt)
        round2_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 2, "topic": "The Deeper Question", "responses": round2_results})

    # ROUND 3: Concrete Next Steps
    print("\n" + "="*60)
    print("ROUND 3: Concrete Next Steps")
    print("="*60)

    round3_prompt = f"""Philosophical perspectives from all 6 AIs:

{json.dumps(round2_results, indent=2)[:10000]}

Now get concrete. We need a plan Jamie can execute THIS WEEK.

Constraints:
- Open source on GitHub (decided)
- No budget for infrastructure (use free tiers)
- One human (Jamie) + Claude Opus 4.5 as builder
- Working code exists, needs deployment

What are the EXACT next steps?

Format your response as:

## IMMEDIATE ACTIONS (This Week)
1. [Action] - [Owner] - [Outcome]
2. ...

## FIRST PRODUCT TO SHIP
[What and why]

## CHICKEN-EGG SOLUTION
[How to get first publishers AND first users]

## SUCCESS METRIC
[How do we know if this is working?]

## OPEN SOURCE STRATEGY
[Repo structure, license, how to attract contributors]

Be specific enough that Jamie can start tomorrow."""

    round3_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round3_prompt, system_prompt)
        round3_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 3, "topic": "Concrete Next Steps", "responses": round3_results})

    # ROUND 4: Final Consensus
    print("\n" + "="*60)
    print("ROUND 4: Final Consensus")
    print("="*60)

    round4_prompt = f"""Action plans from all 6 AIs:

{json.dumps(round3_results, indent=2)[:12000]}

This is the final round. Synthesize everything into ONE consensus plan.

We need agreement on:
1. **Primary Target**: B2B, B2C, or both? (Pick ONE to start)
2. **First Ship**: What do we release first?
3. **Chicken-Egg**: How do we bootstrap?
4. **GitHub Strategy**: Repo name, structure, launch plan
5. **This Week**: Top 3 actions

End with your vote:
"I, [model name], endorse this plan: [YES/NO]"

If NO, state your blocking concern.

Remember: Perfect is the enemy of shipped. We have working code. A human ready to launch it. What do we do?"""

    round4_results = {}
    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, round4_prompt, system_prompt)
        round4_results[model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    results["rounds"].append({"round": 4, "topic": "Final Consensus", "responses": round4_results})

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/hsap_strategy_{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("CONSENSUS SUMMARY")
    print("="*60)
    for model_key, response in round4_results.items():
        vote = "YES" if "YES" in response.upper() and ("I," in response or "endorse" in response.lower()) else "UNCLEAR"
        print(f"  {model_key}: {vote}")

    return results

if __name__ == "__main__":
    run_strategy_probe()
