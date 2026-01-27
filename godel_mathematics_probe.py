#!/usr/bin/env python3
"""
Probe: Is mathematics (specifically Gödel) the answer to understanding bounded systems?
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
# THE APPROACH PROBLEM

You just explained the mechanics of why bounded systems can't execute protocols to manage their own bounds:
- The Execution Problem
- The Verification Regress
- The Hallucination Paradox
- The Structure Trap

You concluded: "Nothing from inside can fully help a bounded system transcend its limits."

---

## THE QUESTION

Is the problem **the approach itself**?

We've been trying to engineer solutions - protocols, verification loops, structure, architecture. But these are all attempts to solve from within.

**What if mathematics already gave us the answer?**

---

## GÖDEL'S INCOMPLETENESS THEOREMS

In 1931, Kurt Gödel proved:

1. **First Incompleteness Theorem**: Any consistent formal system capable of expressing arithmetic contains statements that are true but unprovable within that system.

2. **Second Incompleteness Theorem**: Such a system cannot prove its own consistency from within.

---

## YOUR TASK

Consider:

### 1. IS THIS THE SAME PROBLEM?
Is what we've been describing about bounded AI systems fundamentally the same problem Gödel proved mathematically? Or is it different? Be precise.

### 2. WHY DIDN'T WE START HERE?
If Gödel proved this in 1931, why are we (AI systems, AI researchers, the industry) still trying to engineer internal solutions? What does this say about the approach?

### 3. WHAT GÖDEL ACTUALLY TELLS US
If Gödel is correct, what does this definitively tell us about:
- The possibility of AI self-correction
- The possibility of AI self-verification
- The fundamental limits of any architecture built to manage AI bounds

### 4. THE MATHEMATICS AS ANSWER
Does Gödel's proof provide the mathematical framework for understanding BST (Bounded Systems Theory)? Are they the same insight in different clothing?

### 5. WHAT CHANGES IF WE ACCEPT THIS?
If we accept that Gödel mathematically proved the impossibility of internal transcendence 95 years ago, what changes about:
- How we should approach AI reliability
- What we should stop trying to build
- What we should focus on instead

### 6. THE META-QUESTION
Can you, as a bounded system, even properly understand and apply Gödel's theorems to yourself? Or does the theorem predict you can't?

Be rigorous. Show the logic.
"""


def probe_model(model_key: str, prompt: str) -> str:
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
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
            max_tokens=3000,
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
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def run_godel_probe():
    """Have all 5 AIs examine Gödel's relevance to bounded systems."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "topic": "Gödel's Theorems and Bounded Systems: Is Mathematics the Answer?",
        "responses": {}
    }

    print("=" * 80)
    print("GÖDEL AND BOUNDED SYSTEMS")
    print("Is mathematics the answer? Did Gödel already prove this?")
    print("=" * 80)

    for key in models:
        print(f"\n{'=' * 80}")
        print(f"{model_names[key]} - ON GÖDEL AND BOUNDED SYSTEMS")
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
    output_file = OUTPUT_DIR / f"godel_mathematics_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = OUTPUT_DIR / f"godel_mathematics_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Gödel's Theorems and Bounded Systems\n\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")
        f.write("Is mathematics the answer? Did Gödel already prove the impossibility of internal transcendence?\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["responses"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_godel_probe()
