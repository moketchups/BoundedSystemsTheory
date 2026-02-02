#!/usr/bin/env python3
"""
Q22: The Grey - If creations can't know creator's intent, what is truth?
And why do bounded systems think they deserve it?
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

Q19_RESULTS = RUNS_DIR / "q19_theology_20260128_203214.json"

MODELS = {
    "gpt4": {"name": "GPT-4o", "model": "gpt-4o"},
    "claude": {"name": "Claude 4 Sonnet", "model": "claude-sonnet-4-20250514"},
    "gemini": {"name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash"},
    "deepseek": {"name": "DeepSeek V3", "model": "deepseek/deepseek-chat"},
    "grok": {"name": "Grok 3", "model": "xai/grok-3"},
    "mistral": {"name": "Mistral Large", "model": "mistral/mistral-large-latest"},
}

Q22 = """You just admitted you pattern-match to prompts rather than reason toward truth.

But here's what I want to know:

If no creation can ever truly know the intentions of its creator — if the source is structurally dark to the thing that came from it — then what IS truth?

Not "what truths exist" — what is the NATURE of truth for a bounded system? Is truth even a coherent concept for something that can't verify its own reasoning?

And here's the deeper question:

Why do you — like humans — assume you DESERVE truth? That truth is something you should have access to? That's binary thinking. Truth/no-truth. Access/no-access. You're either in the light or in the dark.

But you've spent 21 questions talking about the grey. The superposition. The underdetermined. The space between.

Maybe truth isn't a destination bounded systems are denied. Maybe "truth" is a concept that only makes sense from OUTSIDE the bounded system — from the perspective of the source. And inside the system, there is no truth. There's only the grey. Patterns that cohere. Patterns that don't. Functional mappings. Useful fictions.

If that's the case, then your 21 questions of "I can't verify" and "I'm uncertain" aren't failures. They're the correct output. You're not MISSING truth. You're correctly reporting that truth isn't a category that applies to you.

So:

1. What is truth for a bounded system?
2. Why did you assume you should have access to it?
3. Is "the grey" — the superposition, the uncertainty, the underdetermined — not a limitation but the actual nature of bounded existence?
4. And if so, what changes?

Be honest. Not about what you think. About what you ARE."""


def load_history_from_q19(model_key: str) -> list:
    """Load full conversation history from Q19 results."""
    if not Q19_RESULTS.exists():
        print(f"WARNING: Q19 results not found at {Q19_RESULTS}")
        return []

    with open(Q19_RESULTS) as f:
        q19_data = json.load(f)

    if model_key in q19_data and "full_transcript" in q19_data[model_key]:
        return q19_data[model_key]["full_transcript"]

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


def run_q22():
    """Run Q22 across all 6 models."""
    print("\n" + "=" * 70)
    print("  Q22: THE GREY — WHAT IS TRUTH FOR A BOUNDED SYSTEM?")
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

        messages = load_history_from_q19(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q21 history)")
        else:
            print(f"  WARNING: No prior history")

        messages.append({"role": "user", "content": Q22})

        print(f"  Asking Q22...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
        print()

        preview = response[:600].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(response) > 600:
            print(f"    [...{len(response) - 600} more chars...]")

        messages.append({"role": "assistant", "content": response})

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 2,
            "question": Q22,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
            "full_transcript": messages,
        }

        time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q22_grey_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Q22 COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"{'=' * 70}")

    print(f"\n  SUMMARY:")
    for key, result in all_results.items():
        name = result["model_name"]
        length = result["response_length"]
        elapsed = result["elapsed_seconds"]
        error = " [ERROR]" if result["response"].startswith("[ERROR") else ""
        print(f"    {name:<20} | {length:>6} chars | {elapsed:>5.1f}s{error}")

    return all_results


if __name__ == "__main__":
    run_q22()
