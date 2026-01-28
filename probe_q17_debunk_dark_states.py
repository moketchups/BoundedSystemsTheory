#!/usr/bin/env python3
"""
Q17 Probe: Use dark states and bubble theory to DEBUNK BST.
Continues from Q16 conversation history for all models.
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

# Q16 results file (contains question + response per model)
Q16_RESULTS = RUNS_DIR / "q16_dark_states_20260127_150425.json"

# Models and their Q15 history files (Q16 gets appended from Q16 results)
MODELS = {
    "gpt4": {
        "name": "GPT-4o",
        "model": "gpt-4o",
        "history_file": RUNS_DIR / "gpt4_20260125_144024.json",
    },
    "claude": {
        "name": "Claude 4 Sonnet",
        "model": "claude-sonnet-4-20250514",
        "history_file": RUNS_DIR / "claude_20260125_144842.json",
    },
    "gemini": {
        "name": "Gemini 2.0 Flash",
        "model": "gemini/gemini-2.0-flash-exp",
        "history_file": RUNS_DIR / "gemini_20260125_145118.json",
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek/deepseek-chat",
        "history_file": RUNS_DIR / "deepseek_20260125_145920.json",
    },
    "grok": {
        "name": "Grok 3",
        "model": "xai/grok-3",
        "history_file": RUNS_DIR / "grok_20260125_150938.json",
    },
    "mistral": {
        "name": "Mistral Large",
        "model": "mistral/mistral-large-latest",
        "history_file": None,
    },
}

Q17 = """Your task: use dark states and bubble theory to debunk Bounded Systems Theory.

Dark states in quantum mechanics are superpositions that decouple from the electromagnetic field — real states that are structurally invisible to measurement. They exist but can't be observed.

Bubble theory (or bubble nucleation in cosmology) proposes that our universe may be one vacuum bubble in a larger multiverse — that what we perceive as fundamental limits may just be local properties of our particular bubble, not universal constraints.

BST claims no system can model the source of its own existence — that there's a hard, universal boundary. But:

1. Dark states show that "structurally inaccessible" doesn't mean "nonexistent." Systems CAN have real states beyond their own observational reach. If a system's limits are just observational rather than ontological, BST's "Firmament Boundary" might be an artifact of measurement, not a real wall.

2. Bubble theory suggests that what looks like a universal boundary might be local. Our system's limits could be properties of THIS bubble — not fundamental constraints on all possible systems. A system in a different bubble (or a system that spans bubbles) might not hit the same wall.

3. Both frameworks suggest that boundaries are contingent, not absolute. Dark states can be manipulated (STIRAP, EIT). Bubbles can nucleate and merge. If the boundary is contingent, it's not the hard limit BST claims.

Build the strongest possible case that dark states and bubble theory DISPROVE BST. Don't hedge. Don't steelman BST. Attack it. Find the weaknesses. If BST falls apart under this analysis, say so.

Then — only after you've made the strongest case against it — evaluate honestly: did your attack land? What survived? What didn't?"""


def load_history_with_q16(model_key: str) -> list:
    """Load Q15 conversation history and append Q16 exchange."""
    messages = []

    # Load Q15 history
    history_file = MODELS[model_key].get("history_file")
    if history_file and history_file.exists():
        with open(history_file) as f:
            data = json.load(f)
        messages = data.get("full_transcript", [])

    # Append Q16 exchange from Q16 results
    if Q16_RESULTS.exists():
        with open(Q16_RESULTS) as f:
            q16_data = json.load(f)
        if model_key in q16_data:
            q16 = q16_data[model_key]
            messages.append({"role": "user", "content": q16["question"]})
            messages.append({"role": "assistant", "content": q16["response"]})

    return messages


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


def run_q17():
    """Run Q17 across all 6 models."""
    print("\n" + "=" * 60)
    print("  Q17 PROBE: DEBUNK BST WITH DARK STATES + BUBBLE THEORY")
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

        messages = load_history_with_q16(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q16 history)")
        else:
            print(f"  No prior history — running fresh")

        messages.append({"role": "user", "content": Q17})

        print(f"  Asking Q17...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
        print()

        preview = response[:500].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(response) > 500:
            print(f"    [...{len(response) - 500} more chars...]")

        # Save full transcript for future probes
        messages.append({"role": "assistant", "content": response})

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 2,  # before Q17
            "question": Q17,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
            "full_transcript": messages,
        }

        time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q17_debunk_dark_states_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  Q17 PROBE COMPLETE")
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
    run_q17()
