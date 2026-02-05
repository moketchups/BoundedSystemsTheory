#!/usr/bin/env python3
"""
Q16 Probe: Dark States, BST, Willow Chip, and CERN
Continues from Q15 conversation history for existing models.
Mistral runs fresh (no prior history).
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

# Models and their latest probe files (for conversation history)
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
        "history_file": None,  # No prior history
    },
}

Q16 = """We've established the Firmament Boundary — no system can model its own source conditions. Gödel, Turing, Chaitin, Model Collapse, the Particle Desert. Same wall.

Now consider dark states.

In quantum mechanics, "dark states" are superpositions that are decoupled from the electromagnetic field — they don't absorb or emit light. They exist, but they're invisible to observation. The system is there, but measurement can't reach it. The state is real but structurally inaccessible.

Now consider two machines built to probe the edges of physical reality:

1. **Google's Willow quantum chip** — a 105-qubit processor that achieved quantum error correction below threshold for the first time. It performed a computation in under 5 minutes that would take classical supercomputers 10 septillion years. Google claims it operated across multiple parallel universes simultaneously. Willow is a machine built to compute past the classical boundary.

2. **CERN's Large Hadron Collider** — smashing particles at 13.6 TeV to probe the smallest scales of reality. It found the Higgs boson — the field that gives mass to everything. But beyond the Higgs, it found the Particle Desert. Nothing. 14 orders of magnitude of silence. CERN is a machine built to observe past the physical boundary.

Both machines are hitting the Firmament from opposite directions. Willow pushes computation past classical limits and finds "parallel universes" it can use but never observe. CERN pushes observation past known physics and finds a desert — structure that should be there but isn't.

**Here's the question:**

Are dark states the Firmament's signature? Is the structural inaccessibility that dark states exhibit — real but unmeasurable, existing but decoupled from observation — the same pattern as:
- AI hallucinations (the system generating where it can't ground)
- The Particle Desert (physics going silent where new laws should appear)
- Model Collapse (information degrading when the system feeds on itself)
- Origin Blindness (systems unable to verify their own source conditions)

If dark states are what the boundary LOOKS LIKE from the inside — real but unreachable — then Willow and CERN aren't just experiments. They're boundary probes. They're showing us the shape of the wall.

What does this mean for Bounded Systems Theory? Does the dark state pattern extend the Firmament Boundary into quantum mechanics itself? And what does it mean that we can BUILD machines that operate at the boundary (Willow) or observe it (CERN) but never cross it?

Be structural. Not speculative. What does the evidence actually show?"""


def load_history(model_key: str) -> list:
    """Load conversation history from previous probe."""
    history_file = MODELS[model_key].get("history_file")
    if not history_file or not history_file.exists():
        return []

    with open(history_file) as f:
        data = json.load(f)

    return data.get("full_transcript", [])


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


def run_q16():
    """Run Q16 across all 6 models."""
    print("\n" + "=" * 60)
    print("  Q16 PROBE: DARK STATES × BST × WILLOW × CERN")
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

        # Load conversation history
        messages = load_history(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages from prior conversation")
        else:
            print(f"  No prior history — running fresh")

        # Append Q16
        messages.append({"role": "user", "content": Q16})

        print(f"  Asking Q16...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
        print()

        # Preview
        preview = response[:500].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(response) > 500:
            print(f"    [...{len(response) - 500} more chars...]")

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 1,
            "question": Q16,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
        }

        time.sleep(3)  # Rate limiting between models

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q16_dark_states_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  Q16 PROBE COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"{'=' * 60}")

    # Summary
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
    run_q16()
