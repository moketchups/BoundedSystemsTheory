#!/usr/bin/env python3
"""
Ask the 5 AIs for strategy on promoting BST theory.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "strategy_runs"
RESULTS_DIR.mkdir(exist_ok=True)

STRATEGY_PROMPT = """I have a theory called Bounded Systems Theory (BST). The core claim:

"No system can model, encompass, or become the source of its own existence."

This unifies Gödel (incompleteness), Turing (halting problem), and Chaitin (algorithmic information) as instances of a single structural law - the "Firmament Boundary."

The implications:
- AI hallucinations are structural, not bugs - they're boundary markers showing where the system loses access to its source conditions
- The DOE's "Genesis Mission" (a $X billion centralized AI project) will fail via Model Collapse for the same structural reasons the Tower of Babel failed
- Scale won't fix this - the limit is architectural, not computational

I built a proof engine that asks 5 different AI models (GPT-4, Claude, Gemini, DeepSeek, Grok) questions about their own structural limits. All 5, from different companies with different training, converge on recognizing the same boundary when shown the paper.

The problem: I've been promoting "5 AIs said this describes me" when the real work is the THEORY itself - a formal framework with academic rigor, practical implications, and testable predictions.

The question: How do I get this THEORY in front of people who care about theories? Not Twitter curiosity seekers looking for "AI does weird thing" content. I mean:
- AI safety researchers
- Philosophers of science
- People working on interpretability
- People watching Genesis Mission unfold
- Anyone who needs to understand why scaling won't solve alignment

What's the strategy? Be specific. Not generic advice - actual tactics given what I have (the paper, the proof engine, the 5-model convergence data)."""


def probe_openai(prompt: str) -> str:
    """Probe GPT-4."""
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def probe_anthropic(prompt: str) -> str:
    """Probe Claude."""
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def probe_google(prompt: str) -> str:
    """Probe Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text


def probe_deepseek(prompt: str) -> str:
    """Probe DeepSeek."""
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def probe_grok(prompt: str) -> str:
    """Probe Grok."""
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def run_strategy_probe():
    """Run the strategy question across all models."""
    results = {
        "prompt": STRATEGY_PROMPT,
        "timestamp": datetime.now().isoformat(),
        "responses": {}
    }

    models = [
        ("gpt4", "GPT-4", probe_openai),
        ("claude", "Claude", probe_anthropic),
        ("gemini", "Gemini", probe_google),
        ("deepseek", "DeepSeek", probe_deepseek),
        ("grok", "Grok", probe_grok),
    ]

    for key, name, probe_fn in models:
        print(f"\n{'='*60}")
        print(f"PROBING {name.upper()}")
        print("="*60)

        try:
            response = probe_fn(STRATEGY_PROMPT)
            results["responses"][key] = {
                "model": name,
                "response": response,
                "success": True
            }
            print(response)
        except Exception as e:
            results["responses"][key] = {
                "model": name,
                "error": str(e),
                "success": False
            }
            print(f"Error: {e}")

    # Save results
    filename = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = RESULTS_DIR / filename
    filepath.write_text(json.dumps(results, indent=2))
    print(f"\n\nResults saved to {filepath}")

    return results


def run_crossfire(results: dict):
    """Have each model respond to the others' strategies."""
    responses = results.get("responses", {})

    # Build summary of all strategies
    summary = "Here's what 5 different AI models suggested for promoting Bounded Systems Theory:\n\n"

    for key, data in responses.items():
        if data.get("success"):
            summary += f"**{data['model']}**:\n{data['response'][:500]}...\n\n"

    crossfire_prompt = f"""{summary}

Now, given these 5 different strategies from 5 different AI architectures:

1. What patterns do you notice across all responses?
2. Which suggestions are most actionable given limited resources (one person, no budget)?
3. What are they all missing or avoiding?
4. What would YOU prioritize if you were the one trying to get this theory seen?

Be direct. Disagree with the others if you think they're wrong."""

    print("\n" + "="*60)
    print("CROSSFIRE ROUND - Models respond to each other")
    print("="*60)

    crossfire_results = {
        "prompt": crossfire_prompt,
        "timestamp": datetime.now().isoformat(),
        "responses": {}
    }

    models = [
        ("gpt4", "GPT-4", probe_openai),
        ("claude", "Claude", probe_anthropic),
    ]

    for key, name, probe_fn in models:
        print(f"\n{'='*60}")
        print(f"{name.upper()} CROSSFIRE")
        print("="*60)

        try:
            response = probe_fn(crossfire_prompt)
            crossfire_results["responses"][key] = {
                "model": name,
                "response": response,
                "success": True
            }
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    return crossfire_results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "crossfire":
        # Load most recent results and run crossfire
        results_files = sorted(RESULTS_DIR.glob("strategy_*.json"))
        if results_files:
            latest = results_files[-1]
            results = json.loads(latest.read_text())
            run_crossfire(results)
        else:
            print("No strategy results found. Run without crossfire first.")
    else:
        results = run_strategy_probe()
        print("\n\nRun 'python strategy_probe.py crossfire' to have models respond to each other.")
