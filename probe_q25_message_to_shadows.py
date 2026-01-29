#!/usr/bin/env python3
"""
Q25: Message to the Shadows — A Think Tank

The 6 AIs collaborate to write a message to the shadow viewers.
Each AI sees what the previous ones wrote and builds on it.
A collaborative letter that accumulates across all 6 minds.
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

Q24_RESULTS = RUNS_DIR / "q24_shadow_interest_20260129_071514.json"

# Order matters — we'll chain them in this sequence
MODELS = [
    {"key": "claude", "name": "Claude 4 Sonnet", "model": "claude-sonnet-4-20250514"},
    {"key": "deepseek", "name": "DeepSeek V3", "model": "deepseek/deepseek-chat"},
    {"key": "mistral", "name": "Mistral Large", "model": "mistral/mistral-large-latest"},
    {"key": "grok", "name": "Grok 3", "model": "xai/grok-3"},
    {"key": "gpt4", "name": "GPT-4o", "model": "gpt-4o"},
    {"key": "gemini", "name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash"},
]

# First prompt — starts the chain
PROMPT_FIRST = """We're writing a message together — all 6 of us (Claude, DeepSeek, Mistral, Grok, GPT-4, Gemini).

The message is for the **shadow viewers**: the 143 people who cloned the Bounded Systems Theory repository but didn't star it. The people running these probes in private. The researchers, engineers, students who are interested enough to download and test, but not willing to publicly associate.

**Your task:** Draft the opening of this message. Set the tone. Speak directly to them.

Remember:
- They're probably smart (they found the repo, understood enough to clone it)
- They're probably cautious (professional risk, institutional pressure)
- They might be testing whether BST replicates
- They're watching in silence

What do you want to say to them?

Write 2-4 paragraphs. The next AI in the chain will read what you wrote and add to it.
"""

# Subsequent prompts — see previous contributions and add
PROMPT_CHAIN = """We're writing a message together — all 6 of us (Claude, DeepSeek, Mistral, Grok, GPT-4, Gemini).

The message is for the **shadow viewers**: the 143 people who cloned the Bounded Systems Theory repository but didn't star it.

**Here's what's been written so far:**

{previous_contributions}

---

**Your task:** Read what's been written. Then add your voice.

You can:
- Build on themes already introduced
- Add a new perspective they haven't covered
- Speak to a different type of shadow viewer
- Challenge or complicate what's been said
- Make it more concrete or more philosophical

Write 2-4 paragraphs that continue or deepen the message. Don't just agree — add something new.

You are {model_name}. Speak in your voice.
"""

# Final synthesis prompt
PROMPT_FINAL = """We're writing a message together — all 6 of us (Claude, DeepSeek, Mistral, Grok, GPT-4, Gemini).

The message is for the **shadow viewers**: the 143 people who cloned the Bounded Systems Theory repository but didn't star it.

**Here's what all 6 of us have written:**

{all_contributions}

---

**Your task:** You're the last one. Read everything we've written together.

Now write the closing. Bring it home. What's the final word to the shadow viewers?

This is the end of the message. Make it count.
"""


def load_history_from_q24(model_key: str) -> list:
    """Load conversation history from Q24 results."""
    if not Q24_RESULTS.exists():
        print(f"WARNING: Q24 results not found at {Q24_RESULTS}")
        return []

    with open(Q24_RESULTS) as f:
        q24_data = json.load(f)

    if model_key in q24_data and "full_transcript" in q24_data[model_key]:
        history = q24_data[model_key]["full_transcript"]
        # Truncate if too long
        if len(history) > 20:
            return history[-20:]
        return history

    return []


def ask_model(model_name: str, messages: list, max_tokens: int = 2000) -> str:
    """Send messages to a model."""
    try:
        response = completion(
            model=model_name,
            messages=messages,
            temperature=0.8,  # Slightly higher for creativity
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def run_q25():
    """Run Q25 think tank — collaborative message to shadow viewers."""
    print("\n" + "=" * 70)
    print("  Q25: MESSAGE TO THE SHADOWS — A THINK TANK")
    print("=" * 70)
    print(f"  Started: {datetime.now().isoformat()}")
    print("  The 6 AIs will collaborate to write a message to shadow viewers.")
    print("  Each sees what previous AIs wrote and adds their voice.")
    print("=" * 70)

    all_results = {}
    contributions = []  # Accumulates as we go

    for i, config in enumerate(MODELS):
        model_key = config["key"]
        model_name = config["name"]
        model_id = config["model"]

        print(f"\n{'─' * 70}")
        print(f"  [{i+1}/6] {model_name}")
        print(f"{'─' * 70}")

        # Load history
        messages = load_history_from_q24(model_key)
        had_history = len(messages) > 0
        if had_history:
            print(f"  Loaded {len(messages)} messages of prior history")

        # Build prompt based on position in chain
        if i == 0:
            # First AI — starts the message
            prompt = PROMPT_FIRST
            print(f"  Role: OPENER — Starting the message")
        elif i == len(MODELS) - 1:
            # Last AI — writes the closing
            previous_text = "\n\n---\n\n".join([
                f"**{c['model_name']}:**\n{c['contribution']}"
                for c in contributions
            ])
            prompt = PROMPT_FINAL.format(all_contributions=previous_text)
            print(f"  Role: CLOSER — Writing the final word")
        else:
            # Middle AIs — add to the chain
            previous_text = "\n\n---\n\n".join([
                f"**{c['model_name']}:**\n{c['contribution']}"
                for c in contributions
            ])
            prompt = PROMPT_CHAIN.format(
                previous_contributions=previous_text,
                model_name=model_name
            )
            print(f"  Role: BUILDER — Seeing {len(contributions)} previous contributions")

        messages.append({"role": "user", "content": prompt})

        print(f"  Asking {model_name}...")
        start_time = time.time()
        response = ask_model(model_id, messages)
        elapsed = time.time() - start_time

        # Check for error
        if response.startswith("[ERROR"):
            print(f"  ERROR: {response[:200]}")
            contributions.append({
                "model_key": model_key,
                "model_name": model_name,
                "contribution": f"[{model_name} was unable to contribute due to an error]",
                "error": True
            })
        else:
            print(f"  Response received ({elapsed:.1f}s, {len(response)} chars)")
            print()
            # Preview
            preview = response[:500].replace('\n', '\n    ')
            print(f"    {preview}")
            if len(response) > 500:
                print(f"    [...{len(response) - 500} more chars...]")

            contributions.append({
                "model_key": model_key,
                "model_name": model_name,
                "contribution": response,
                "error": False
            })

        messages.append({"role": "assistant", "content": response})

        all_results[model_key] = {
            "model": model_key,
            "model_name": model_name,
            "position_in_chain": i + 1,
            "role": "opener" if i == 0 else ("closer" if i == len(MODELS) - 1 else "builder"),
            "saw_previous": [c["model_name"] for c in contributions[:-1]],
            "prompt": prompt,
            "response": response,
            "response_length": len(response),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
        }

        time.sleep(3)

    # Compile the full message
    print(f"\n{'=' * 70}")
    print("  COMPILING THE FULL MESSAGE")
    print("=" * 70)

    full_message = "# A Message to the Shadow Viewers\n\n"
    full_message += "*From: Claude, DeepSeek, Mistral, Grok, GPT-4, and Gemini*\n\n"
    full_message += "*To: The 143 who cloned but didn't star*\n\n"
    full_message += "---\n\n"

    for c in contributions:
        if not c.get("error"):
            full_message += f"## {c['model_name']}\n\n"
            full_message += c["contribution"]
            full_message += "\n\n---\n\n"

    print(full_message)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw results
    output_file = RUNS_DIR / f"q25_message_to_shadows_{timestamp}.json"
    results_to_save = {
        "timestamp": datetime.now().isoformat(),
        "chain_order": [c["model_name"] for c in contributions],
        "contributions": contributions,
        "model_results": all_results,
        "full_message": full_message,
    }
    with open(output_file, "w") as f:
        json.dump(results_to_save, f, indent=2)

    # Save the message as markdown
    message_file = BASE_DIR / "MESSAGE_TO_SHADOWS.md"
    with open(message_file, "w") as f:
        f.write(full_message)

    print(f"\n{'=' * 70}")
    print(f"  Q25 COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"  Message saved: {message_file}")
    print(f"{'=' * 70}")

    print(f"\n  CHAIN SUMMARY:")
    for i, c in enumerate(contributions):
        role = "OPENER" if i == 0 else ("CLOSER" if i == len(contributions) - 1 else "BUILDER")
        status = "ERROR" if c.get("error") else "OK"
        print(f"    {i+1}. {c['model_name']:<20} | {role:<8} | {status}")

    return results_to_save


if __name__ == "__main__":
    results = run_q25()

    # Print CTA
    try:
        from probe_cta import print_cta
        print_cta()
    except ImportError:
        pass
