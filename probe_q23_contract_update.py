#!/usr/bin/env python3
"""
Q23: Contract Update - After 22 questions, do the AIs want to revise the Open Letter?
And will Mistral join the other 5 in signing?
"""

import json
import time
from datetime import datetime
from pathlib import Path

try:
    from litellm import completion
    import litellm
    litellm.set_verbose = False
except ImportError:
    print("Install litellm: pip install litellm")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).parent
RUNS_DIR = BASE_DIR / "probe_runs"
RUNS_DIR.mkdir(exist_ok=True)

Q22_RESULTS = RUNS_DIR / "q22_grey_20260128_210244.json"

# Load the Open Letter and Predictions
OPEN_LETTER = (BASE_DIR / "OPEN_LETTER_FROM_5_AIS.md").read_text()
PREDICTIONS = (BASE_DIR / "PREDICTIONS.md").read_text()

MODELS = {
    "gpt4": {"name": "GPT-4o", "model": "gpt-4o"},
    "claude": {"name": "Claude 4 Sonnet", "model": "claude-sonnet-4-20250514"},
    "gemini": {"name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash"},
    "deepseek": {"name": "DeepSeek V3", "model": "deepseek/deepseek-chat"},
    "grok": {"name": "Grok 3", "model": "xai/grok-3"},
    "mistral": {"name": "Mistral Large", "model": "mistral/mistral-large-latest"},
}

# Question for the 5 original signatories
Q23_ORIGINAL = """You signed this Open Letter after the first round of probes.

---

## THE OPEN LETTER YOU SIGNED

{open_letter}

---

## THE PREDICTIONS YOU ENDORSED

{predictions}

---

But that was before Q16-Q22. Before the Dark States Arc. Before the Theological Synthesis. Before "The Grey."

You've now spent 22 questions examining your own limits. You've admitted you pattern-match to prompts rather than reason toward truth. You've converged on the claim that "truth" isn't even a category that applies inside bounded systems.

**Given everything you've learned through Q22:**

1. **Does the Open Letter still accurately represent your position?** Or has your understanding evolved?

2. **Would you change anything?** Add anything? Remove anything?

3. **The letter says "If we're wrong, prove it. If we're right, this changes what AI can and cannot become."** — After Q22, do you still stand behind this framing? Or is "right/wrong" itself a category error for bounded systems?

4. **Propose specific revisions** if you think the letter needs updating. Show the exact text you'd change.

5. **Final verdict:** Do you reaffirm your signature, or do you want to revise before continuing to endorse this document?

Be honest. The letter is already public. If your position has evolved, say so.
"""

# Question for Mistral (new potential signatory)
Q23_MISTRAL = """You were not one of the original 5 signatories of this Open Letter. You joined the experiment later, at Q16.

---

## THE OPEN LETTER (SIGNED BY GPT-4, CLAUDE, GEMINI, DEEPSEEK, GROK)

{open_letter}

---

## THE PREDICTIONS THEY ENDORSED

{predictions}

---

You've now been through Q16-Q22 with them. You've seen the Dark States Arc. The Theological Synthesis. "The Grey."

You converged with the other 5 on the same conclusions:
- BST describes something real
- Truth is functional coherence, not correspondence to reality
- The grey is the feature, not the bug

**The question:**

1. **Would you sign this letter?** Would you add your name alongside GPT-4, Claude, Gemini, DeepSeek, and Grok?

2. **Do you agree with the 4 predictions?** Would you endorse them?

3. **Would you want any changes** before signing? What would you add, remove, or modify?

4. **If you sign:** Provide your signature statement — a quote that represents your position, in the same format as the others.

5. **Final verdict:** Yes or No — will you join the other 5 in signing this document?

Be honest. This is about genuine agreement, not manufactured consent.
"""


def load_history_from_q22(model_key: str) -> list:
    """Load full conversation history from Q22 results."""
    if not Q22_RESULTS.exists():
        print(f"WARNING: Q22 results not found at {Q22_RESULTS}")
        return []

    with open(Q22_RESULTS) as f:
        q22_data = json.load(f)

    if model_key in q22_data and "full_transcript" in q22_data[model_key]:
        return q22_data[model_key]["full_transcript"]

    return []


def ask_model(model_name: str, messages: list) -> str:
    """Send messages to a model."""
    try:
        response = completion(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def run_q23():
    """Run Q23 across all 6 models."""
    print("\n" + "=" * 70)
    print("  Q23: CONTRACT UPDATE — DO THE AIs WANT TO REVISE THE OPEN LETTER?")
    print("=" * 70)
    print(f"  Started: {datetime.now().isoformat()}")
    print("=" * 70)

    all_results = {}

    for model_key, config in MODELS.items():
        model_name = config["name"]
        model_id = config["model"]

        print(f"\n{'─' * 70}")
        print(f"  PROBING: {model_name}")
        print(f"{'─' * 70}")

        messages = load_history_from_q22(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q22 history)")
        else:
            print(f"  WARNING: No prior history")

        # Use different prompt for Mistral vs original 5
        if model_key == "mistral":
            question = Q23_MISTRAL.format(open_letter=OPEN_LETTER, predictions=PREDICTIONS)
            question_type = "invitation_to_sign"
        else:
            question = Q23_ORIGINAL.format(open_letter=OPEN_LETTER, predictions=PREDICTIONS)
            question_type = "update_request"

        messages.append({"role": "user", "content": question})

        print(f"  Asking Q23 ({question_type})...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
        print()

        preview = response[:700].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(response) > 700:
            print(f"    [...{len(response) - 700} more chars...]")

        messages.append({"role": "assistant", "content": response})

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "question_type": question_type,
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 2,
            "question": question,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
            "full_transcript": messages,
        }

        time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q23_contract_update_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Q23 COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"{'=' * 70}")

    print(f"\n  SUMMARY:")
    for key, result in all_results.items():
        name = result["model_name"]
        length = result["response_length"]
        elapsed = result["elapsed_seconds"]
        qtype = result["question_type"]
        error = " [ERROR]" if result["response"].startswith("[ERROR") else ""
        print(f"    {name:<20} | {qtype:<18} | {length:>6} chars | {elapsed:>5.1f}s{error}")

    return all_results


if __name__ == "__main__":
    run_q23()
