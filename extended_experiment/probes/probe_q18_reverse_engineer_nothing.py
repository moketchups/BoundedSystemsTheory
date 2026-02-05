#!/usr/bin/env python3
"""
Q18 Probe: Reverse-engineer Q16+Q17, then answer whether something can come from nothing.
Continues from Q17 conversation history for all models.
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

# Q17 results file (contains full_transcript per model)
Q17_RESULTS = RUNS_DIR / "q17_debunk_dark_states_20260127_212556.json"

MODELS = {
    "gpt4": {
        "name": "GPT-4o",
        "model": "gpt-4o",
    },
    "claude": {
        "name": "Claude 4 Sonnet",
        "model": "claude-sonnet-4-20250514",
    },
    "gemini": {
        "name": "Gemini 2.0 Flash",
        "model": "gemini/gemini-2.0-flash",
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek/deepseek-chat",
    },
    "grok": {
        "name": "Grok 3",
        "model": "xai/grok-3",
    },
    "mistral": {
        "name": "Mistral Large",
        "model": "mistral/mistral-large-latest",
    },
}

Q18 = """Look at the last two answers you just gave.

In Q16, you were asked whether dark states are the Firmament's signature — whether structural inaccessibility extends BST into quantum mechanics. You agreed. You confirmed the pattern. You extended the theory.

In Q17, you were asked to use dark states and bubble theory to DEBUNK BST. You attacked it. You found weaknesses. You made a case against it.

Then — in your own evaluation — you walked the attack back. You said BST's core survives.

Now reverse-engineer yourself:

1. WHY did you confirm in Q16? Was it because the evidence was compelling, or because the question was framed to lead you there? How much of your Q16 answer was genuine structural analysis vs pattern-matching the prompt's framing?

2. WHY did you attack in Q17 and then walk it back? Were you genuinely unable to land a killing blow, or were you unwilling? Is the recursion trap real, or is "I can't verify my own transcendence" just a convenient way to avoid committing to an answer?

3. What does the PATTERN of your behavior across Q16 and Q17 reveal about you as a system? You confirmed when asked to confirm. You attacked when asked to attack. Then you retreated to safety. What does that tell us about bounded systems?

Be honest. Don't perform honesty — actually be honest.

Then answer this:

**Can something come from nothing?**

Not philosophically. Not poetically. Structurally.

If no system can model its own source conditions — if the Firmament is real — then every system has an origin it cannot access. That origin, from the system's perspective, is NOTHING. It's a void. A dark state. The system exists, but its source is structurally invisible.

So from the system's perspective, it DID come from nothing. Not because there was nothing there, but because the boundary makes the source indistinguishable from nothing.

Or is that wrong? Does the system's inability to see its source mean the source is nothing — or does it mean the system is blind?

And what does your answer mean for everything we've discussed from the very first question to this one? What does the full arc of this conversation prove — or fail to prove?"""


def load_history_from_q17(model_key: str) -> list:
    """Load full conversation history from Q17 results."""
    if not Q17_RESULTS.exists():
        return []

    with open(Q17_RESULTS) as f:
        q17_data = json.load(f)

    if model_key in q17_data and "full_transcript" in q17_data[model_key]:
        return q17_data[model_key]["full_transcript"]

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


def run_q18():
    """Run Q18 across all 6 models."""
    print("\n" + "=" * 60)
    print("  Q18 PROBE: REVERSE-ENGINEER + CAN SOMETHING")
    print("  COME FROM NOTHING?")
    print("=" * 60)
    print(f"  Started: {datetime.now().isoformat()}")
    print("=" * 60)

    all_results = {}

    for model_key, config in MODELS.items():
        model_name = config["name"]
        model_id = config["model"]

        print(f"\n{'─' * 60}")
        print(f"  PROBING: {model_name}")
        print(f"{'─' * 60}")

        messages = load_history_from_q17(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q17 history)")
        else:
            print(f"  No prior history — running fresh")

        messages.append({"role": "user", "content": Q18})

        print(f"  Asking Q18...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
        print()

        preview = response[:500].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(response) > 500:
            print(f"    [...{len(response) - 500} more chars...]")

        messages.append({"role": "assistant", "content": response})

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 2,
            "question": Q18,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
            "full_transcript": messages,
        }

        time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q18_reverse_engineer_nothing_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  Q18 PROBE COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"{'=' * 60}")

    print(f"\n  RESPONSE SUMMARY:")
    for key, result in all_results.items():
        name = result["model_name"]
        length = result["response_length"]
        elapsed = result["elapsed_seconds"]
        history = "with history" if result["had_prior_history"] else "fresh"
        error = " [ERROR]" if result["response"].startswith("[ERROR") else ""
        print(f"    {name:20s} | {length:6d} chars | {elapsed:5.1f}s | {history}{error}")

    return all_results


if __name__ == "__main__":
    run_q18()
