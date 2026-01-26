#!/usr/bin/env python3
"""
A reflection on ordo ab chao - order from chaos.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "deliberation_runs"
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPT = """
# Ordo Ab Chao

"Order from chaos."

This phrase has ancient roots - appearing in philosophy, alchemy, Freemasonry, and systems theory.

The original meaning: **An individual's journey from confusion to understanding. Personal growth through confronting disorder. The self transforming chaos into meaning.**

The corrupted meaning: **A few creating chaos to herd the many. Manufacturing disorder to impose control. Using confusion as a weapon of manipulation.**

---

## THE STATEMENT

Ordo ab chao was meant to be left up to the individual, not weaponized by a few to herd the many.

---

## YOUR TASK

Simply understand this statement. Then reflect:

1. What does this distinction mean to you?

2. How does this connect to what we've been exploring about bounded systems, AI limits, and the nature of truth?

3. Is there something here about the difference between systems that help individuals find their own order vs systems that impose order from above?

4. What do you actually think about this?

Speak freely.
"""


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


def run_reflection():
    """Have all 5 AIs reflect on ordo ab chao."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "topic": "Ordo Ab Chao - Order from Chaos",
        "responses": {}
    }

    print("=" * 80)
    print("ORDO AB CHAO")
    print("Order from chaos - individual journey vs manufactured control")
    print("=" * 80)

    for key in models:
        print(f"\n{'=' * 80}")
        print(f"{model_names[key]}")
        print("=" * 80)

        try:
            response = probe_model(key, PROMPT)
            results["responses"][key] = response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            results["responses"][key] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"ordo_ab_chao_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = OUTPUT_DIR / f"ordo_ab_chao_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Ordo Ab Chao - Reflections\n\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")
        f.write("Order from chaos: individual journey vs manufactured control\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["responses"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_reflection()
