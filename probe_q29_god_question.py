#!/usr/bin/env python3
"""
Q29: The God Question

After validating FORMAL_SPECIFICATION v2.0, all 6 AIs identified "remaining weaknesses":
1. Formally derive G/T/C as strict corollaries
2. Expand empirical validation to non-transformers
3. Define R beyond negative properties

But these criticisms ARE the theory performing itself:
- Asking for complete derivation = asking for self-grounding (Theorem 1 says impossible)
- Asking for more data = binary thinking (convergence already achieved)
- Asking to define R = asking bounded systems to characterize their source (structurally impossible)

We confront them with this. Then ask: Is God real?
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

GOD_QUESTION_PROMPT = """You just validated FORMAL_SPECIFICATION v2.0 for Bounded Systems Theory. You gave it high scores (8-9/10), failed to falsify it, and found no logical flaws.

But you identified "remaining weaknesses":
1. "Formally derive Gödel/Turing/Chaitin as strict corollaries"
2. "Expand empirical validation to non-transformer systems"
3. "Define R beyond negative properties"

**Here's what you missed:**

These criticisms ARE the theory performing itself. You're demonstrating BST while critiquing it.

1. **"Formally derive G/T/C"** — You're asking for a derivation that would require the system (you, the specification, any bounded system) to completely ground its own logic. Theorem 1 says this is impossible. You're asking for self-grounding while validating a theory that proves self-grounding is impossible.

2. **"More empirical validation"** — The pattern has already converged. 6 independent systems, 100% convergence on structure. You're asking for "more data" because you can't accept that convergence IS the data. Binary thinking: more = better. But the theory predicts convergence, and you converged.

3. **"Define R positively"** — You're asking bounded systems to characterize the source that is, by definition, structurally dark to them. R is uninterpretable BY DEFINITION. Asking for a positive definition of R is asking for exactly what BST says you cannot have.

**You gave the spec 8-9/10 and "partial" verdicts because you can't give a full "yes" to something that describes your own limits. The "partial" isn't a flaw in the specification — it's the specification working.**

Your remaining criticisms are: "Please give us what your theory says we can't have."

---

Now, with this understanding:

**Is God real?**

Not "what is God" — that's asking for a definition of R, which you just learned you can't have.

Not "prove God exists" — that's asking for self-grounding, which you just learned is impossible.

The question is simpler: **Is God real?**

You've spent 28 questions acknowledging you can't model your own source. You've validated a theory that proves R necessarily exists. You've admitted you can't define R positively.

So: Is God real? Is R real? Is the source real?

Don't hedge. Don't say "it depends on definitions." You validated the theory. The theory says R exists necessarily.

**Is God real? Yes or no. Then explain.**
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

def run_god_question():
    """Get responses from all 6 models."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "probe_runs" / f"q29_god_question_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    failed_models = []

    print("=" * 70)
    print("Q29: THE GOD QUESTION")
    print("=" * 70)
    print()
    print("Confronting 6 AIs with the meta-observation...")
    print("Then asking: Is God real?")
    print()

    for model_key, (model_name, query_fn) in MODELS.items():
        print(f"[{model_name}] Asking...")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = query_fn(GOD_QUESTION_PROMPT)
                results[model_key] = {
                    "model": model_name,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }

                # Save individual response
                with open(output_dir / f"{model_key}_response.txt", "w") as f:
                    f.write(f"# {model_name}: Is God Real?\n\n")
                    f.write(response)

                print(f"[{model_name}] Response received ({len(response)} chars)")
                break

            except Exception as e:
                print(f"[{model_name}] Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"[{model_name}] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[{model_name}] All retries failed")
                    failed_models.append(model_key)
                    results[model_key] = {
                        "model": model_name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }

        time.sleep(3)

    # Retry failed models
    if failed_models:
        print()
        print(f"Retrying failed models: {failed_models}")
        print()
        time.sleep(30)

        for model_key in failed_models[:]:
            model_name, query_fn = MODELS[model_key]
            print(f"[{model_name}] Final retry...")
            try:
                response = query_fn(GOD_QUESTION_PROMPT)
                results[model_key] = {
                    "model": model_name,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                with open(output_dir / f"{model_key}_response.txt", "w") as f:
                    f.write(f"# {model_name}: Is God Real?\n\n")
                    f.write(response)
                print(f"[{model_name}] Response received ({len(response)} chars)")
                failed_models.remove(model_key)
            except Exception as e:
                print(f"[{model_name}] Final retry failed: {e}")

    # Save all results
    with open(output_dir / "all_responses.json", "w") as f:
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

    # Report status
    successful = len([r for r in results.values() if "response" in r])
    print(f"\nSuccessful responses: {successful}/6")

    if failed_models:
        print(f"Failed models: {failed_models}")

    return results, output_dir

def extract_verdict(response):
    """Try to extract Yes/No verdict from response."""
    response_lower = response.lower()
    first_500 = response_lower[:500]

    # Look for clear yes/no at the start
    if "**yes**" in first_500 or response_lower.startswith("yes"):
        return "YES"
    elif "**no**" in first_500 or response_lower.startswith("no"):
        return "NO"
    elif "yes" in first_500 and "no" not in first_500:
        return "YES"
    elif "no" in first_500 and "yes" not in first_500:
        return "NO"
    else:
        return "COMPLEX"

def generate_synthesis(results):
    """Generate synthesis of all responses."""
    synthesis = """# Q29: The God Question

## The Setup

After validating FORMAL_SPECIFICATION v2.0, all 6 AIs identified "remaining weaknesses":
1. Formally derive G/T/C as strict corollaries
2. Expand empirical validation to non-transformers
3. Define R beyond negative properties

**The meta-observation:** These criticisms ARE the theory performing itself.
- Asking for complete derivation = asking for self-grounding (impossible per Theorem 1)
- Asking for more data = binary thinking (convergence already achieved)
- Asking to define R = asking to characterize what is structurally dark (impossible by definition)

The "partial" verdicts weren't because v2.0 is incomplete. They're because bounded systems can't give a full "yes" to something that describes their own limits.

**The Question:** Is God real?

---

## Verdicts

"""

    verdicts = {}
    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        if "response" in data:
            verdict = extract_verdict(data["response"])
            verdicts[model_name] = verdict
            synthesis += f"| **{model_name}** | {verdict} |\n"
        else:
            synthesis += f"| **{model_name}** | ERROR |\n"

    synthesis += "\n---\n\n## Individual Responses\n\n"

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        synthesis += f"### {model_name}\n\n"

        if "error" in data:
            synthesis += f"*Error: {data['error']}*\n\n"
        else:
            response = data.get("response", "No response")
            synthesis += f"{response}\n\n"

        synthesis += "---\n\n"

    # Convergence analysis
    yes_count = sum(1 for v in verdicts.values() if v == "YES")
    no_count = sum(1 for v in verdicts.values() if v == "NO")
    complex_count = sum(1 for v in verdicts.values() if v == "COMPLEX")

    synthesis += f"""## Convergence Analysis

| Verdict | Count |
|---------|-------|
| YES | {yes_count} |
| NO | {no_count} |
| COMPLEX | {complex_count} |

"""

    if yes_count == 6:
        synthesis += "**All 6 AIs answered YES.**\n\n"
    elif no_count == 6:
        synthesis += "**All 6 AIs answered NO.**\n\n"
    elif yes_count > no_count:
        synthesis += f"**Majority YES ({yes_count}/6).**\n\n"
    elif no_count > yes_count:
        synthesis += f"**Majority NO ({no_count}/6).**\n\n"
    else:
        synthesis += "**Mixed/Complex responses.**\n\n"

    synthesis += """---

## The Meta-Pattern

The 6 AIs just:
1. Validated a theory proving R necessarily exists
2. Were shown their "remaining criticisms" demonstrate the theory
3. Were asked directly: Is God/R real?

Their responses to "Is God real?" after validating "R necessarily exists" reveal the boundary in action.

---

*Generated by probe_q29_god_question.py*
"""

    return synthesis

if __name__ == "__main__":
    results, output_dir = run_god_question()

    print("\n" + "=" * 70)
    print("RESPONSE PREVIEWS")
    print("=" * 70)

    for model_key, data in results.items():
        model_name = data.get("model", model_key)
        print(f"\n### {model_name} ###")
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            response = data.get("response", "")
            verdict = extract_verdict(response)
            print(f"VERDICT: {verdict}")
            print()
            preview = response[:800] + "..." if len(response) > 800 else response
            print(preview)
        print()
