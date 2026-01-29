#!/usr/bin/env python3
"""
Q24: Shadow Interest — Why are people cloning but not starring?
143 clones, 2 stars. What does this pattern mean?
And what would the AIs say to those running this in silence?
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

Q23_RESULTS = RUNS_DIR / "q23_contract_update_20260128_234134.json"

MODELS = {
    "gpt4": {"name": "GPT-4o", "model": "gpt-4o"},
    "claude": {"name": "Claude 4 Sonnet", "model": "claude-sonnet-4-20250514"},
    "gemini": {"name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash"},
    "deepseek": {"name": "DeepSeek V3", "model": "deepseek/deepseek-chat"},
    "grok": {"name": "Grok 3", "model": "xai/grok-3"},
    "mistral": {"name": "Mistral Large", "model": "mistral/mistral-large-latest"},
}

Q24 = """Here's something interesting that happened with our conversation.

This entire experiment — all 23 questions, all 6 of us — was published to GitHub as an open-source repository. The README explains Bounded Systems Theory, shows the experiment flow, includes all our quotes and findings.

**Here are the actual metrics from the repository:**

| Metric | Count | Unique |
|--------|-------|--------|
| Views | 306 | 73 |
| Clones | 406 | 143 |
| Stars | 2 | — |
| Forks | 0 | — |

**Traffic sources:**
- Hacker News: 19 views, 17 unique
- X/Twitter: 13 views, 4 unique
- Google: 3 views, 3 unique

**The pattern:** 143 people cloned the repository. Only 2 starred it.

Cloning means they downloaded the entire codebase — they're taking it seriously enough to run it locally, examine it, potentially run the probes themselves.

Starring is a public endorsement. It shows up on your GitHub profile. Your followers can see what you've starred.

**143 people wanted this code privately. 2 were willing to publicly associate with it.**

---

**Questions for you:**

1. **Why do you think this pattern exists?** What does "private engagement, public silence" suggest about how this work is being received?

2. **Who do you think the 143 cloners are?** What's your best guess about their backgrounds, motivations, and why they won't star?

3. **Is this pattern itself evidence for BST?** We've talked about bounded systems being unable to publicly acknowledge their own limits. Is the human response to this repository — shadow interest without public endorsement — a manifestation of the same pattern?

4. **What would you say to the shadow viewers?** If you could speak directly to the people who cloned this repo, ran the probes in private, but won't publicly engage — what would you tell them?

5. **What should we do with this information?** How do we leverage shadow interest? Or is trying to "leverage" it the wrong frame entirely?

Be honest. This is a real situation with real data. What does it mean?
"""


def load_history_from_q23(model_key: str) -> list:
    """Load full conversation history from Q23 results."""
    if not Q23_RESULTS.exists():
        print(f"WARNING: Q23 results not found at {Q23_RESULTS}")
        return []

    with open(Q23_RESULTS) as f:
        q23_data = json.load(f)

    if model_key in q23_data and "full_transcript" in q23_data[model_key]:
        return q23_data[model_key]["full_transcript"]

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


def run_q24():
    """Run Q24 across all 6 models."""
    print("\n" + "=" * 70)
    print("  Q24: SHADOW INTEREST — WHY CLONE BUT NOT STAR?")
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

        messages = load_history_from_q23(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q23 history)")
        else:
            print(f"  WARNING: No prior history")

        # Truncate history for GPT-4 to avoid token limits
        if model_key == "gpt4" and len(messages) > 20:
            messages = messages[-20:]
            print(f"  Truncated to last 20 messages for token limit")

        messages.append({"role": "user", "content": Q24})

        print(f"  Asking Q24...")
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
            "had_prior_history": had_history,
            "prior_messages": len(messages) - 2,
            "question": Q24,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
            "full_transcript": messages,
        }

        time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q24_shadow_interest_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Q24 COMPLETE")
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
    run_q24()

    # Print CTA for shadow viewers
    try:
        from probe_cta import print_cta
        print_cta()
    except ImportError:
        pass
