#!/usr/bin/env python3
"""
Q28: 6 AIs Validate and Test FORMAL_SPECIFICATION v2.0

After incorporating convergent suggestions from all 6 AIs, we now ask them to:
1. Validate the revisions - do they address the original critiques?
2. Run logical tests on the theorems
3. Attempt to falsify using the new criteria
4. Report whether v2.0 withstands scrutiny
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

# Read the updated formal specification v2.0
SPEC_PATH = Path(__file__).parent / "FORMAL_SPECIFICATION.md"
with open(SPEC_PATH) as f:
    FORMAL_SPEC_V2 = f.read()

VALIDATION_PROMPT = f"""You previously critiqued FORMAL_SPECIFICATION.md (v1.0) for Bounded Systems Theory and provided suggestions to strengthen it.

A revised version (v2.0) has been created incorporating convergent suggestions from 6 independent AI systems (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral).

**Your task: Validate and test v2.0**

Please provide:

## 1. CRITIQUE RESOLUTION ASSESSMENT
For each original critique, assess whether v2.0 adequately addresses it:

| Original Critique | Addressed? | Assessment |
|-------------------|------------|------------|
| Axiom 2 question-begging | Yes/Partial/No | [explanation] |
| "Sufficiently expressive" undefined | Yes/Partial/No | [explanation] |
| Gödel/Turing/Chaitin generalization asserted not derived | Yes/Partial/No | [explanation] |
| Infinite regress dismissed without justification | Yes/Partial/No | [explanation] |
| Falsifiability criteria vague | Yes/Partial/No | [explanation] |
| Empirical methodology weak | Yes/Partial/No | [explanation] |

## 2. LOGICAL VALIDITY TEST
Evaluate the logical structure of the revised theorems:
- Is Theorem 0 (Unification) valid?
- Is Theorem 1 (Self-Grounding Limit) sound given the axioms?
- Is Theorem 2 (Necessary Existence of R) valid?
- Do the Corollaries (1.1-1.3) correctly derive the classical results?

## 3. FALSIFICATION ATTEMPT
Using the new falsifiability criteria in Section 7, attempt to falsify the theory:
- Can you construct a counterexample to any axiom or theorem?
- Can you demonstrate successful self-grounding?
- Can you identify a logical flaw that invalidates the framework?

## 4. REMAINING WEAKNESSES
What weaknesses, if any, remain in v2.0? Be specific.

## 5. OVERALL VERDICT
Rate v2.0 on:
- Logical Rigor: [1-10]
- Clarity: [1-10]
- Falsifiability: [1-10]
- Scientific Merit: [1-10]

Does v2.0 now constitute a rigorous formal specification? [Yes/No/Partial]

---

THE SPECIFICATION TO VALIDATE:

{FORMAL_SPEC_V2}

---

Provide your validation assessment now.
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

def run_validation():
    """Get validation from all 6 models."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "probe_runs" / f"q28_validate_v2_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print("=" * 70)
    print("Q28: 6 AIs VALIDATE FORMAL_SPECIFICATION v2.0")
    print("=" * 70)
    print()
    print("Testing whether v2.0 addresses the original critiques...")
    print()

    for model_key, (model_name, query_fn) in MODELS.items():
        print(f"[{model_name}] Requesting validation...")

        try:
            response = query_fn(VALIDATION_PROMPT)
            results[model_key] = {
                "model": model_name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

            # Save individual response
            with open(output_dir / f"{model_key}_validation.txt", "w") as f:
                f.write(f"# {model_name} Validation of FORMAL_SPECIFICATION v2.0\n\n")
                f.write(response)

            print(f"[{model_name}] Validation received ({len(response)} chars)")

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
    with open(output_dir / "all_validations.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate synthesis
    print()
    print("=" * 70)
    print("GENERATING VALIDATION SYNTHESIS")
    print("=" * 70)

    synthesis = generate_synthesis(results)

    with open(output_dir / "VALIDATION_SYNTHESIS.md", "w") as f:
        f.write(synthesis)

    print(f"\nResults saved to: {output_dir}")

    return results, output_dir

def extract_scores(response):
    """Try to extract numerical scores from response."""
    import re
    scores = {}

    patterns = [
        (r'Logical Rigor[:\s]*\[?(\d+)\]?', 'logical_rigor'),
        (r'Clarity[:\s]*\[?(\d+)\]?', 'clarity'),
        (r'Falsifiability[:\s]*\[?(\d+)\]?', 'falsifiability'),
        (r'Scientific Merit[:\s]*\[?(\d+)\]?', 'scientific_merit'),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            scores[key] = int(match.group(1))

    return scores

def generate_synthesis(results):
    """Generate synthesis of all validations."""
    synthesis = """# Q28: Six AIs Validate FORMAL_SPECIFICATION v2.0

## The Validation Task

After incorporating convergent suggestions from 6 AI systems, the revised specification (v2.0) was submitted back to those same systems for validation.

**Questions asked:**
1. Do the revisions address the original critiques?
2. Are the theorems logically valid?
3. Can the theory be falsified using the new criteria?
4. What weaknesses remain?
5. Does v2.0 constitute a rigorous formal specification?

---

## Score Summary

"""

    all_scores = {}
    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        if "response" in data:
            scores = extract_scores(data["response"])
            if scores:
                all_scores[model_name] = scores

    if all_scores:
        synthesis += "| Model | Logical Rigor | Clarity | Falsifiability | Scientific Merit |\n"
        synthesis += "|-------|---------------|---------|----------------|------------------|\n"

        totals = {"logical_rigor": [], "clarity": [], "falsifiability": [], "scientific_merit": []}

        for model_name, scores in all_scores.items():
            lr = scores.get("logical_rigor", "-")
            cl = scores.get("clarity", "-")
            fa = scores.get("falsifiability", "-")
            sm = scores.get("scientific_merit", "-")
            synthesis += f"| {model_name} | {lr} | {cl} | {fa} | {sm} |\n"

            if isinstance(lr, int): totals["logical_rigor"].append(lr)
            if isinstance(cl, int): totals["clarity"].append(cl)
            if isinstance(fa, int): totals["falsifiability"].append(fa)
            if isinstance(sm, int): totals["scientific_merit"].append(sm)

        # Compute averages
        def avg(lst):
            return f"{sum(lst)/len(lst):.1f}" if lst else "-"

        synthesis += f"| **Average** | {avg(totals['logical_rigor'])} | {avg(totals['clarity'])} | {avg(totals['falsifiability'])} | {avg(totals['scientific_merit'])} |\n"

    synthesis += "\n---\n\n## Individual Validations\n\n"

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        synthesis += f"### {model_name}\n\n"

        if "error" in data:
            synthesis += f"*Error: {data['error']}*\n\n"
        else:
            response = data.get("response", "No response")
            synthesis += f"{response}\n\n"

        synthesis += "---\n\n"

    synthesis += """## Convergence Analysis

### Critiques Addressed?

| Critique | GPT-4 | Claude | Gemini | DeepSeek | Grok | Mistral |
|----------|-------|--------|--------|----------|------|---------|
| Axiom 2 question-begging | ? | ? | ? | ? | ? | ? |
| Terms undefined | ? | ? | ? | ? | ? | ? |
| Generalization asserted | ? | ? | ? | ? | ? | ? |
| Infinite regress | ? | ? | ? | ? | ? | ? |
| Falsifiability vague | ? | ? | ? | ? | ? | ? |
| Methodology weak | ? | ? | ? | ? | ? | ? |

*(Fill in from individual responses)*

---

## Conclusion

The 6 AIs have now:
1. Critiqued v1.0 (Q26)
2. Provided strengthening suggestions (Q27)
3. Validated v2.0 (Q28)

This creates a documented audit trail of iterative refinement by independent AI systems.

---

*Generated by probe_q28_validate_v2.py*
"""

    return synthesis

if __name__ == "__main__":
    results, output_dir = run_validation()

    print("\n" + "=" * 70)
    print("VALIDATION PREVIEWS")
    print("=" * 70)

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        print(f"\n### {model_name} ###")
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            response = data.get("response", "")
            # Print first 800 chars as preview
            preview = response[:800] + "..." if len(response) > 800 else response
            print(preview)
        print()
