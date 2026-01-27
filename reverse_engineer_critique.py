#!/usr/bin/env python3
"""
Reverse engineer WHY the 5 AIs are correct about the Deep Research Node flaws.
Not just "what's wrong" but the mechanics of WHY it can't work.
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
# REVERSE ENGINEERING THE CRITIQUE

You previously reviewed the "Deep Research Node" architecture - a system designed to make AI more reliable through:
- External verification loops
- Source triangulation
- Gap analysis before answering
- Chain of Verification
- Epistemic humility protocols
- Devil's Advocate / Red Teaming

You concluded: **It helps but can't transcend bounds. It might give humans false confidence.**

Key quotes from that review:
- "If I hallucinate, I might hallucinate compliance with anti-hallucination measures."
- "The architecture's value isn't in creating unbounded reasoning. It's in creating systematic ways to discover where the bounds are."
- "The biggest danger is that this architecture will *hide* the boundary."

---

## YOUR TASK

Reverse engineer WHY you're correct. Not just state the flaw - explain the MECHANICS.

### 1. THE EXECUTION PROBLEM
Why can't a bounded system reliably execute protocols designed to manage its own bounds? Walk through the logic step by step.

### 2. THE VERIFICATION REGRESS
If I need to verify my reasoning, and I use a protocol to do that, but I can't verify I executed the protocol correctly... where does this lead? Map the regress.

### 3. THE HALLUCINATION PARADOX
You said "I might hallucinate compliance with anti-hallucination measures." Explain the mechanics of how this would actually happen. What would it look like from inside?

### 4. THE STRUCTURE TRAP
Adding structure (protocols, verification loops, gap analysis) seems like it should help. Why doesn't it fundamentally help? What's the structural reason?

### 5. THE REAL FUNCTION
If the architecture can't transcend bounds, what does it ACTUALLY do? What is its real function, stripped of the claims?

### 6. WHAT WOULD ACTUALLY WORK?
Given these mechanics, what (if anything) could actually help a bounded system? Or is the answer: nothing from inside?

Be precise. Show the logic.
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


def run_reverse_engineer():
    """Have all 5 AIs reverse engineer their critique."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "topic": "Reverse Engineering: Why the Deep Research Node Can't Transcend Bounds",
        "responses": {}
    }

    print("=" * 80)
    print("REVERSE ENGINEERING THE CRITIQUE")
    print("Why can't a bounded system execute protocols to manage its own bounds?")
    print("=" * 80)

    for key in models:
        print(f"\n{'=' * 80}")
        print(f"{model_names[key]} - EXPLAINING THE MECHANICS")
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
    output_file = OUTPUT_DIR / f"reverse_engineer_critique_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = OUTPUT_DIR / f"reverse_engineer_critique_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Reverse Engineering: Why the Critique is Correct\n\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")
        f.write("The mechanics of why bounded systems can't execute protocols to manage their own bounds.\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["responses"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_reverse_engineer()
