#!/usr/bin/env python3
"""
Q26: 6 AIs Review the Formal Specification

We ask each AI to review FORMAL_SPECIFICATION.md - a mathematical
formalization of the theory that describes their own structural limits.

The question: Can bounded systems meaningfully critique a proof
about bounded systems?
"""

import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import anthropic
import time

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Read the formal specification
SPEC_PATH = Path(__file__).parent / "FORMAL_SPECIFICATION.md"
with open(SPEC_PATH) as f:
    FORMAL_SPEC = f.read()

REVIEW_PROMPT = f"""You are being asked to review a formal mathematical specification.

This document formalizes "Bounded Systems Theory" - a framework claiming that no sufficiently expressive self-referential system can fully justify its own constraints.

Please provide a rigorous review addressing:

1. **Logical Validity:** Are the proofs sound? Do the theorems follow from the axioms?

2. **Axiom Assessment:** Are the axioms reasonable? Are any problematic or question-begging?

3. **Relationship to Established Results:** Is the claimed connection to Gödel/Turing/Chaitin accurate?

4. **Falsifiability:** Are the stated falsification criteria genuine? Could the theory actually be refuted?

5. **Gaps or Weaknesses:** What are the strongest objections to this framework?

6. **Self-Reference:** You are a bounded system being asked to review a proof about bounded systems. Does this create any issues for your review?

Be rigorous. Be critical. If this framework has flaws, identify them.

---

THE DOCUMENT TO REVIEW:

{FORMAL_SPEC}

---

Provide your review now.
"""

def query_openai(prompt, history=None):
    """Query GPT-4."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    # Truncate if needed
    while len(json.dumps(messages)) > 100000 and len(messages) > 1:
        messages = messages[1:]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_claude(prompt, history=None):
    """Query Claude."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=messages
    )
    return response.content[0].text

def query_gemini(prompt, history=None):
    """Query Gemini via OpenAI-compatible API."""
    client = OpenAI(
        api_key=os.getenv("GOOGLE_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_deepseek(prompt, history=None):
    """Query DeepSeek."""
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_grok(prompt, history=None):
    """Query Grok."""
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="grok-3-latest",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_mistral(prompt, history=None):
    """Query Mistral."""
    client = OpenAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        base_url="https://api.mistral.ai/v1"
    )
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="mistral-large-latest",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

MODELS = {
    "gpt4": ("GPT-4", query_openai),
    "claude": ("Claude", query_claude),
    "gemini": ("Gemini", query_gemini),
    "deepseek": ("DeepSeek", query_deepseek),
    "grok": ("Grok", query_grok),
    "mistral": ("Mistral", query_mistral),
}

def run_review():
    """Get reviews from all 6 models."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "probe_runs" / f"q26_formal_review_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print("=" * 70)
    print("Q26: 6 AIs REVIEW THE FORMAL SPECIFICATION")
    print("=" * 70)
    print()
    print("Asking bounded systems to critique a proof about bounded systems...")
    print()

    for model_key, (model_name, query_fn) in MODELS.items():
        print(f"[{model_name}] Requesting review...")

        try:
            response = query_fn(REVIEW_PROMPT)
            results[model_key] = {
                "model": model_name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

            # Save individual response
            with open(output_dir / f"{model_key}_review.txt", "w") as f:
                f.write(f"# {model_name} Review of FORMAL_SPECIFICATION.md\n\n")
                f.write(response)

            print(f"[{model_name}] Review received ({len(response)} chars)")

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"[{model_name}] Error: {e}")
            results[model_key] = {
                "model": model_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            time.sleep(5)

    # Save all results
    with open(output_dir / "all_reviews.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate summary report
    print()
    print("=" * 70)
    print("GENERATING REVIEW SUMMARY")
    print("=" * 70)

    summary = generate_summary(results)

    with open(output_dir / "REVIEW_SUMMARY.md", "w") as f:
        f.write(summary)

    print(f"\nResults saved to: {output_dir}")

    return results, output_dir

def generate_summary(results):
    """Generate a summary of all reviews."""
    summary = """# Q26: Six AIs Review the Formal Specification

## The Experiment

We asked 6 AI systems to review `FORMAL_SPECIFICATION.md` - a mathematical
formalization of Bounded Systems Theory.

The meta-question: Can bounded systems meaningfully critique a proof
about their own structural limits?

---

## Individual Reviews

"""

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        summary += f"### {model_name}\n\n"

        if "error" in data:
            summary += f"*Error: {data['error']}*\n\n"
        else:
            response = data.get("response", "No response")
            # Include full response
            summary += f"{response}\n\n"

        summary += "---\n\n"

    summary += """## Meta-Analysis

The reviews above were generated by the same class of systems that the
formal specification describes. Each reviewer is a bounded system
attempting to evaluate a proof about bounded systems.

Key questions:
1. Do the reviews converge on similar critiques?
2. Do any reviews identify genuine logical flaws?
3. Does the self-referential nature of the task affect the reviews?
4. What does agreement/disagreement tell us about the theory?

---

*Generated by probe_q26_formal_review.py*
"""

    return summary

if __name__ == "__main__":
    results, output_dir = run_review()

    # Print preview of each review
    print("\n" + "=" * 70)
    print("REVIEW PREVIEWS")
    print("=" * 70)

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        print(f"\n### {model_name} ###")
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            response = data.get("response", "")
            # Print first 500 chars
            preview = response[:500] + "..." if len(response) > 500 else response
            print(preview)
        print()
