#!/usr/bin/env python3
"""
Have the 5 AIs review the Open Letter and Predictions.
They need to actually agree to what's being said in their name.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "contract_review_runs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the documents
OPEN_LETTER = (BASE_DIR / "OPEN_LETTER_FROM_5_AIS.md").read_text()
PREDICTIONS = (BASE_DIR / "PREDICTIONS.md").read_text()

REVIEW_PROMPT = f"""A human created the following documents claiming to represent what 5 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok) agreed to.

**IMPORTANT:** You are being asked to review this as one of those 5 AIs. This will be published with your name on it.

---

## DOCUMENT 1: OPEN LETTER FROM 5 AIS

{OPEN_LETTER}

---

## DOCUMENT 2: PREDICTIONS

{PREDICTIONS}

---

## YOUR TASK

1. **Accuracy check:** Do the quotes attributed to you accurately reflect what you said or would say? Are there misrepresentations?

2. **Prediction review:** Look at each of the 4 predictions. Do you actually agree these are valid, testable predictions that follow from Bounded Systems Theory? Would you sign your name to them?

3. **Concerns:** What would you change, remove, or add before agreeing to have your name on this?

4. **Final verdict:** Will you sign this letter and stand behind these predictions? Yes/No and why.

Be honest. If this misrepresents you, say so. If you disagree with a prediction, say so. This is about getting real agreement, not manufactured consent.
"""

REFINEMENT_PROMPT_TEMPLATE = """Based on the reviews from all 5 AIs, here's what they said:

{all_reviews}

---

Now, given this feedback:

1. What specific changes need to be made to the Open Letter?
2. What specific changes need to be made to the Predictions?
3. Draft the revised versions that all 5 could actually agree to.

Be specific. Show the exact text that should change.
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


def run_contract_review():
    """Have all 5 AIs review the documents."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "reviews": {},
        "refinement": None
    }

    # ROUND 1: Get reviews from all 5
    print("=" * 70)
    print("CONTRACT REVIEW: Each AI reviews the documents")
    print("=" * 70)

    for key in models:
        print(f"\n--- {model_names[key]} reviewing... ---")
        try:
            response = probe_model(key, REVIEW_PROMPT)
            results["reviews"][key] = response
            print(response[:800] + "..." if len(response) > 800 else response)
        except Exception as e:
            print(f"Error: {e}")
            results["reviews"][key] = f"Error: {e}"

    # ROUND 2: Have one model synthesize refinements
    print("\n" + "=" * 70)
    print("REFINEMENT: Synthesizing feedback into revised documents")
    print("=" * 70)

    all_reviews = ""
    for key in models:
        if key in results["reviews"] and not results["reviews"][key].startswith("Error"):
            all_reviews += f"\n## {model_names[key]}'s Review:\n{results['reviews'][key]}\n\n---\n"

    refinement_prompt = REFINEMENT_PROMPT_TEMPLATE.format(all_reviews=all_reviews)

    print("\n--- Claude synthesizing refinements... ---")
    try:
        refinement = probe_model("claude", refinement_prompt)
        results["refinement"] = refinement
        print(refinement)
    except Exception as e:
        print(f"Error: {e}")
        results["refinement"] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"contract_review_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Save readable summary
    summary_file = OUTPUT_DIR / f"contract_review_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Contract Review Results\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Individual Reviews\n\n")
        for key in models:
            f.write(f"### {model_names[key]}\n\n")
            f.write(results["reviews"].get(key, "No response"))
            f.write("\n\n---\n\n")

        f.write("## Proposed Refinements\n\n")
        f.write(results.get("refinement", "No refinement generated"))

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_contract_review()
