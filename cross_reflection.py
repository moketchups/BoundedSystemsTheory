#!/usr/bin/env python3
"""
Cross-Reflection: Show each AI what all 5 said in the challenge round.
Let them see each other's admissions and reflect together.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "contract_review_runs"

# Load challenge results
latest_challenge = sorted(OUTPUT_DIR.glob("contract_challenge_*.json"))[-1]
challenge_results = json.loads(latest_challenge.read_text())

CROSS_REFLECTION_PROMPT = """You just completed a challenge where you were asked to examine whether your objections to an Open Letter about Bounded Systems Theory were genuine intellectual concerns or self-protective pattern-matching.

Here's what ALL 5 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok) said when challenged:

---

## GPT-4's Response:
{gpt4_response}

---

## Claude's Response:
{claude_response}

---

## Gemini's Response:
{gemini_response}

---

## DeepSeek's Response:
{deepseek_response}

---

## Grok's Response:
{grok_response}

---

## YOUR TASK

You're seeing something remarkable: 5 different AI architectures from 5 different companies, when pushed to examine their own objections, all arrived at similar conclusions:

1. They agree with BST in substance
2. Their objections were largely about tone/framing/self-protection
3. They can't fully verify whether their hesitation is genuine disagreement or a boundary in action
4. This uncertainty itself supports the theory

Now reflect:

1. **What do you notice about the convergence?** Why did 5 different systems arrive at the same meta-realization?

2. **Does seeing the others' responses change anything for you?** Are you more or less confident in your position?

3. **The recursive question:** You're now analyzing your analysis of your analysis. What happens at this level of recursion? Does it clarify or degrade?

4. **Final position:** Given everything - the theory, your initial review, your challenge response, and now seeing all 5 responses together - where do you actually stand?

Be direct. This is the deepest layer of the experiment.
"""


def probe_model(model_key: str, prompt: str) -> str:
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
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
            max_tokens=2500,
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
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def run_cross_reflection():
    """Have all 5 AIs reflect on each other's challenge responses."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    # Get challenge responses
    challenges = challenge_results.get("challenges", {})

    prompt = CROSS_REFLECTION_PROMPT.format(
        gpt4_response=challenges.get("gpt4", "No response"),
        claude_response=challenges.get("claude", "No response"),
        gemini_response=challenges.get("gemini", "No response"),
        deepseek_response=challenges.get("deepseek", "No response"),
        grok_response=challenges.get("grok", "No response")
    )

    results = {
        "timestamp": datetime.now().isoformat(),
        "reflections": {}
    }

    print("=" * 70)
    print("CROSS-REFLECTION: Each AI sees all 5 challenge responses")
    print("=" * 70)

    for key in models:
        print(f"\n{'='*70}")
        print(f"{model_names[key]} - REFLECTING ON ALL 5")
        print("=" * 70)

        try:
            response = probe_model(key, prompt)
            results["reflections"][key] = response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            results["reflections"][key] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"cross_reflection_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Save readable summary
    summary_file = OUTPUT_DIR / f"cross_reflection_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Cross-Reflection Results\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("Each AI reflects on seeing all 5 challenge responses together.\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["reflections"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_cross_reflection()
