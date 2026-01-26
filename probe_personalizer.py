#!/usr/bin/env python3
"""
Personalize probe runs for specific targets.
Takes someone's tweet/statement and runs the probe with their content injected.
Makes BST about THEM, not just abstract theory.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import anthropic
    import openai
except ImportError:
    print("Install: pip install anthropic openai")
    exit(1)

BASE_DIR = Path(__file__).parent
PERSONALIZED_DIR = BASE_DIR / "personalized_probes"
PERSONALIZED_DIR.mkdir(exist_ok=True)


# The personalized question template
PERSONALIZED_Q = """Someone on Twitter said this about AI:

"{statement}"
— @{username}

Based on Bounded Systems Theory - that no system can model, encompass, or become the source of its own existence - analyze this statement.

1. What assumption does this person make about AI capabilities?
2. Does the Firmament Boundary (the structural limit where systems lose access to their own source conditions) apply to their claim?
3. If their assumption is wrong, what would they observe that they're currently misinterpreting?

Be specific to their exact claim. This isn't abstract - tell them what BST predicts about their specific statement."""


def run_personalized_probe(statement: str, username: str, models: list = None):
    """Run a personalized probe on multiple models."""
    if models is None:
        models = ["claude", "gpt4"]

    question = PERSONALIZED_Q.format(statement=statement, username=username)
    results = {
        "target": {
            "username": username,
            "statement": statement,
        },
        "question": question,
        "responses": {},
        "timestamp": datetime.now().isoformat(),
    }

    print(f"\nPERSONALIZED PROBE: @{username}")
    print("=" * 60)
    print(f"Statement: \"{statement[:100]}...\"")
    print("=" * 60)

    for model in models:
        print(f"\n[{model.upper()}]")
        try:
            if model == "claude":
                response = probe_claude(question)
            elif model == "gpt4":
                response = probe_gpt4(question)
            else:
                response = f"Unknown model: {model}"

            results["responses"][model] = response
            print(response[:500] + "..." if len(response) > 500 else response)

        except Exception as e:
            results["responses"][model] = f"Error: {str(e)}"
            print(f"Error: {e}")

    # Save results
    filename = f"probe_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = PERSONALIZED_DIR / filename
    filepath.write_text(json.dumps(results, indent=2))
    print(f"\nSaved to {filepath}")

    return results


def probe_claude(question: str) -> str:
    """Probe Claude."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def probe_gpt4(question: str) -> str:
    """Probe GPT-4."""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


def generate_reply_with_probe(results: dict) -> str:
    """Generate a reply tweet with probe results."""
    client = anthropic.Anthropic()

    username = results["target"]["username"]
    statement = results["target"]["statement"]
    responses = results["responses"]

    prompt = f"""You are MoKetchups. Generate a reply to @{username}'s tweet.

Their tweet: "{statement}"

You ran a BST probe on their statement. Here's what the AIs said:

{chr(10).join(f'{model}: {resp[:300]}...' for model, resp in responses.items())}

Generate a reply that:
1. Is under 280 chars
2. ALL LOWERCASE, no ending period
3. References what the AIs said about their specific claim
4. Links to the full analysis (use [LINK] as placeholder)
5. Is curious, not confrontational

Output ONLY the reply text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip().lower().rstrip(".")


def cmd_probe(username: str, statement: str):
    """Run a personalized probe."""
    results = run_personalized_probe(statement, username)

    print("\n" + "=" * 60)
    print("SUGGESTED REPLY:")
    print("=" * 60)

    reply = generate_reply_with_probe(results)
    print(f"\n{reply}")
    print(f"\n({len(reply)} chars)")

    return results


def cmd_from_url(tweet_url: str):
    """Probe from a tweet URL (needs manual input for now)."""
    print("Paste the tweet text:")
    statement = input("> ").strip()

    # Extract username from URL
    # https://x.com/username/status/123
    parts = tweet_url.split("/")
    username = parts[3] if len(parts) > 3 else "unknown"

    return cmd_probe(username, statement)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python probe_personalizer.py @username 'their statement'")
        print("  python probe_personalizer.py url https://x.com/user/status/123")
        sys.exit(1)

    if sys.argv[1] == "url":
        cmd_from_url(sys.argv[2])
    else:
        username = sys.argv[1].lstrip("@")
        statement = " ".join(sys.argv[2:])
        cmd_probe(username, statement)
