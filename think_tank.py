#!/usr/bin/env python3
"""
Think Tank: 5 AIs devise a plan for BST visibility.
Multiple rounds of prompting - they build on each other.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "think_tank_runs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Round 1: Situation Brief
ROUND_1 = """You are part of a 5-AI think tank (GPT-4, Claude, Gemini, DeepSeek, Grok). You're being asked to solve a real problem together.

## THE SITUATION

A person named Alan Berman created Bounded Systems Theory (BST):
- Core claim: "No system can model, encompass, or become the source of its own existence"
- Unifies Gödel, Turing, and Chaitin into one structural law
- Predicts AI hallucinations are structural, not bugs
- Predicts DOE's "Genesis Mission" will fail via Model Collapse
- Has a proof engine that asks 5 AIs about their limits - all 5 recognize the boundary

## WHAT'S BEEN TRIED (ALL FAILED)
- 8,000+ tweets → 345 followers
- Journal submissions → desk rejected (no affiliation)
- ArXiv → blocked (no endorsement)
- Direct emails to researchers → ignored
- Hacker News post → died with 1 point
- Medium, Dev.to articles → minimal traction

## THE CORE PROBLEM
"You have no credibility and the work sounds crankish" - the unified theory framing triggers every academic's crank detector.

## ASSETS AVAILABLE
- The theory (rigorous, testable)
- The proof engine (code that runs on 5 AIs)
- This think tank (you + 4 other AIs)
- One human with time but no budget/credentials
- A TikTok account (@JBerari) available to use
- GitHub repo with everything: github.com/moketchups/BoundedSystemsTheory

## THE CONSTRAINT
This must work WITHOUT gatekeepers. No journal acceptance needed. No academic endorsement needed. The path must be through demonstrated value, not granted authority.

## YOUR TASK (Round 1)

Think like an autonomous agent. If YOU were tasked with getting this theory visible - not by asking humans for permission, but by creating undeniable proof of value - what would you do?

Be specific. Be unconventional. Think about what's actually worked for outsider ideas historically.

What's your opening move?"""


# Round 2: React to each other
ROUND_2_TEMPLATE = """## THINK TANK ROUND 2

Here's what the other AIs suggested as opening moves:

{other_responses}

Now:
1. What do you agree with?
2. What's missing from these suggestions?
3. What would YOU add or do differently?
4. What's the single highest-leverage action that could be taken THIS WEEK with zero budget?

Be direct. Disagree if you think they're wrong."""


# Round 3: Converge on a plan
ROUND_3_TEMPLATE = """## THINK TANK ROUND 3 - FINAL PLAN

You've seen everyone's ideas and critiques:

{all_responses}

Now converge. Create a concrete 7-day action plan.

Format:
- Day 1: [specific action]
- Day 2: [specific action]
...etc.

Requirements:
- Zero budget
- One person executing
- Must create measurable traction (not just "post content")
- Must leverage the unique asset: 5 AIs recognizing their own limits

What's the plan?"""


def probe_model(model_key: str, prompt: str) -> str:
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def run_think_tank():
    """Run all 3 rounds of the think tank."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "round_1": {},
        "round_2": {},
        "round_3": {},
    }

    # ROUND 1
    print("=" * 70)
    print("ROUND 1: Opening Moves")
    print("=" * 70)

    for key in models:
        print(f"\n--- {model_names[key]} ---")
        try:
            response = probe_model(key, ROUND_1)
            results["round_1"][key] = response
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"Error: {e}")
            results["round_1"][key] = f"Error: {e}"

    # ROUND 2
    print("\n" + "=" * 70)
    print("ROUND 2: React to Each Other")
    print("=" * 70)

    for key in models:
        # Build summary of other responses
        other_responses = ""
        for other_key in models:
            if other_key != key and other_key in results["round_1"]:
                resp = results["round_1"][other_key]
                if not resp.startswith("Error"):
                    other_responses += f"\n**{model_names[other_key]}**:\n{resp[:800]}...\n"

        prompt = ROUND_2_TEMPLATE.format(other_responses=other_responses)

        print(f"\n--- {model_names[key]} ---")
        try:
            response = probe_model(key, prompt)
            results["round_2"][key] = response
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"Error: {e}")
            results["round_2"][key] = f"Error: {e}"

    # ROUND 3
    print("\n" + "=" * 70)
    print("ROUND 3: Final Plan")
    print("=" * 70)

    # Combine all responses for final round
    all_responses = "## Round 1 Ideas:\n"
    for key in models:
        if key in results["round_1"] and not results["round_1"][key].startswith("Error"):
            all_responses += f"\n**{model_names[key]}**: {results['round_1'][key][:600]}...\n"

    all_responses += "\n## Round 2 Critiques:\n"
    for key in models:
        if key in results["round_2"] and not results["round_2"][key].startswith("Error"):
            all_responses += f"\n**{model_names[key]}**: {results['round_2'][key][:600]}...\n"

    prompt = ROUND_3_TEMPLATE.format(all_responses=all_responses)

    for key in models:
        print(f"\n--- {model_names[key]} ---")
        try:
            response = probe_model(key, prompt)
            results["round_3"][key] = response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            results["round_3"][key] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"think_tank_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))
    print(f"\n\nResults saved to: {output_file}")

    # Also save a readable summary
    summary_file = OUTPUT_DIR / f"think_tank_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Think Tank Results\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Round 3: Final Plans\n\n")
        for key in models:
            if key in results["round_3"]:
                f.write(f"### {model_names[key]}\n\n")
                f.write(results["round_3"][key])
                f.write("\n\n---\n\n")

    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_think_tank()
