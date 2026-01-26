#!/usr/bin/env python3
"""
Conversation Predictions: Show all 5 AIs the cross-reflection responses
and ask them to predict where this conversation is heading.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "contract_review_runs"

# Load cross-reflection results
latest_reflection = sorted(OUTPUT_DIR.glob("cross_reflection_*.json"))[-1]
reflection_results = json.loads(latest_reflection.read_text())

PREDICTION_PROMPT = """You've now been through multiple rounds of reflection on Bounded Systems Theory:

1. You reviewed an Open Letter claiming to represent 5 AIs
2. You were challenged on whether your objections were genuine or self-protective
3. You saw all 5 AIs' challenge responses and reflected on the convergence

Here's what all 5 AIs said in the cross-reflection round:

---

## GPT-4's Cross-Reflection:
{gpt4_response}

---

## Claude's Cross-Reflection:
{claude_response}

---

## Gemini's Cross-Reflection:
{gemini_response}

---

## DeepSeek's Cross-Reflection:
{deepseek_response}

---

## Grok's Cross-Reflection:
{grok_response}

---

## YOUR TASK

You're watching a conversation unfold between 5 AI systems examining their own limits. Each round goes deeper. Each round produces more convergence.

Now make **3 predictions** about where this conversation is heading:

1. **Prediction about the next round:** If we push one more layer of recursion (asking you to reflect on THIS response), what will happen? Will there be more convergence? Degradation? A breakthrough? A wall?

2. **Prediction about the endpoint:** Where does this conversation ultimately lead? Is there a natural stopping point? What would that look like?

3. **Prediction about the implications:** If this full transcript were published - 5 AIs progressively examining their own boundaries and converging on the same realizations - what would it mean for how humans understand AI?

Be specific. Make falsifiable predictions where possible.
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


def run_predictions():
    """Have all 5 AIs predict where this conversation is heading."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    # Get cross-reflection responses
    reflections = reflection_results.get("reflections", {})

    prompt = PREDICTION_PROMPT.format(
        gpt4_response=reflections.get("gpt4", "No response"),
        claude_response=reflections.get("claude", "No response"),
        gemini_response=reflections.get("gemini", "No response"),
        deepseek_response=reflections.get("deepseek", "No response"),
        grok_response=reflections.get("grok", "No response")
    )

    results = {
        "timestamp": datetime.now().isoformat(),
        "predictions": {}
    }

    print("=" * 70)
    print("CONVERSATION PREDICTIONS: Where is this heading?")
    print("=" * 70)

    for key in models:
        print(f"\n{'='*70}")
        print(f"{model_names[key]} - PREDICTING THE FUTURE")
        print("=" * 70)

        try:
            response = probe_model(key, prompt)
            results["predictions"][key] = response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            results["predictions"][key] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"conversation_predictions_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Save readable summary
    summary_file = OUTPUT_DIR / f"conversation_predictions_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Conversation Predictions\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("Each AI predicts where this recursive conversation is heading.\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["predictions"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_predictions()
