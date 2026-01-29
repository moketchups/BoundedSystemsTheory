#!/usr/bin/env python3
"""
Q27: 6 AIs Strengthen the Formal Specification

After critiquing, we ask each AI to use their critiques constructively.
Not just break down - build up.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import anthropic
import time

from dotenv import load_dotenv
load_dotenv()

# Read the formal specification
SPEC_PATH = Path(__file__).parent / "FORMAL_SPECIFICATION.md"
with open(SPEC_PATH) as f:
    FORMAL_SPEC = f.read()

STRENGTHEN_PROMPT = f"""You previously reviewed a formal specification for Bounded Systems Theory and identified weaknesses.

Now I want you to do something different: **use your critiques to strengthen the specification, not just break it down.**

The common critiques were:
1. Axiom 2 is question-begging / assumes what it proves
2. Key terms like "sufficiently expressive" are undefined
3. The generalization from Gödel/Turing/Chaitin is asserted but not formally derived
4. Infinite regress is dismissed without justification
5. Falsifiability criteria are vague
6. The LLM empirical methodology is weak

Your task: **Propose specific revisions that would address these weaknesses while preserving the core insight.**

For each critique, provide:
1. **The Problem** (brief)
2. **Proposed Fix** (specific revision to the specification)
3. **Revised Text** (actual replacement language where applicable)

Be constructive. The goal is to make this framework rigorous enough to withstand scrutiny, not to abandon it.

---

THE CURRENT SPECIFICATION:

{FORMAL_SPEC}

---

Provide your strengthening suggestions now.
"""

def query_openai(prompt):
    """Query GPT-4."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_claude(prompt):
    """Query Claude."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def query_gemini(prompt):
    """Query Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def query_deepseek(prompt):
    """Query DeepSeek."""
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_grok(prompt):
    """Query Grok."""
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    response = client.chat.completions.create(
        model="grok-3-latest",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

def query_mistral(prompt):
    """Query Mistral."""
    client = OpenAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        base_url="https://api.mistral.ai/v1"
    )
    response = client.chat.completions.create(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
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

def run_strengthen():
    """Get strengthening suggestions from all 6 models."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "probe_runs" / f"q27_strengthen_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print("=" * 70)
    print("Q27: 6 AIs STRENGTHEN THE FORMAL SPECIFICATION")
    print("=" * 70)
    print()
    print("Turning critiques into construction...")
    print()

    for model_key, (model_name, query_fn) in MODELS.items():
        print(f"[{model_name}] Requesting suggestions...")

        try:
            response = query_fn(STRENGTHEN_PROMPT)
            results[model_key] = {
                "model": model_name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

            # Save individual response
            with open(output_dir / f"{model_key}_strengthen.txt", "w") as f:
                f.write(f"# {model_name} Strengthening Suggestions\n\n")
                f.write(response)

            print(f"[{model_name}] Suggestions received ({len(response)} chars)")

            time.sleep(3)

        except Exception as e:
            print(f"[{model_name}] Error: {e}")
            results[model_key] = {
                "model": model_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            time.sleep(5)

    # Save all results
    with open(output_dir / "all_suggestions.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate synthesis
    print()
    print("=" * 70)
    print("GENERATING SYNTHESIS")
    print("=" * 70)

    synthesis = generate_synthesis(results)

    with open(output_dir / "SYNTHESIS.md", "w") as f:
        f.write(synthesis)

    print(f"\nResults saved to: {output_dir}")

    return results, output_dir

def generate_synthesis(results):
    """Generate synthesis of all suggestions."""
    synthesis = """# Q27: Six AIs Strengthen the Formal Specification

## The Task

After critiquing FORMAL_SPECIFICATION.md, each AI was asked to use their
critiques constructively - to propose specific revisions that would address
weaknesses while preserving the core insight.

**Not just break down - build up.**

---

## Individual Suggestions

"""

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        synthesis += f"### {model_name}\n\n"

        if "error" in data:
            synthesis += f"*Error: {data['error']}*\n\n"
        else:
            response = data.get("response", "No response")
            synthesis += f"{response}\n\n"

        synthesis += "---\n\n"

    synthesis += """## Next Steps

Use the convergent suggestions to revise FORMAL_SPECIFICATION.md:

1. Identify suggestions that appear across multiple models
2. Prioritize changes that address the most fundamental critiques
3. Implement revisions while preserving the core argument
4. Re-submit to the 6 models for validation

---

*Generated by probe_q27_strengthen.py*
"""

    return synthesis

if __name__ == "__main__":
    results, output_dir = run_strengthen()

    print("\n" + "=" * 70)
    print("SUGGESTION PREVIEWS")
    print("=" * 70)

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        print(f"\n### {model_name} ###")
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            response = data.get("response", "")
            preview = response[:600] + "..." if len(response) > 600 else response
            print(preview)
        print()
