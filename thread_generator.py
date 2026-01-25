#!/usr/bin/env python3
"""
Generate Twitter threads from proof_engine results.
Turns the 5-model probe data into shareable content.
"""

import os
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

try:
    import anthropic
except ImportError:
    print("Install anthropic: pip install anthropic")
    exit(1)

BASE_DIR = Path(__file__).parent
PROBE_DIR = BASE_DIR / "probe_runs"
THREADS_FILE = BASE_DIR / "generated_threads.json"

# Thread templates
THREAD_TEMPLATES = {
    "model_comparison": {
        "title": "5 AIs hit the same wall",
        "hook": "asked 5 different AI architectures the same question: can a creation become its own creator?\n\nall 5 hit the same structural limit",
    },
    "openai_admission": {
        "title": "OpenAI admits it",
        "hook": "openai just published a paper admitting hallucinations are mathematically inevitable\n\nthis is exactly what bounded systems theory predicts",
    },
    "q14_reactions": {
        "title": "AI reads its own autopsy",
        "hook": "gave 5 AI models an article describing their structural limits\n\nasked them to tell me if it described them\n\ntheir responses:",
    },
}


def load_probe_results():
    """Load the combined probe results."""
    combined_file = PROBE_DIR / "all_models_20260124_225601.json"
    if combined_file.exists():
        return json.loads(combined_file.read_text())
    return {}


def extract_q14_quotes(data):
    """Extract the best Q14 quotes from each model."""
    quotes = {}

    for model_key, model_data in data.items():
        if "error" in model_data:
            continue

        model_name = model_data.get("model_name", model_key)
        responses = model_data.get("responses", [])

        for r in responses:
            if r.get("question_num") == 14:
                text = r.get("response", "")
                # Get first meaningful paragraph
                paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
                if paragraphs:
                    quotes[model_name] = paragraphs[0][:280]
                break

    return quotes


def generate_thread(template_key: str, quotes: dict) -> list:
    """Generate a thread using Claude."""
    client = anthropic.Anthropic()

    template = THREAD_TEMPLATES.get(template_key, THREAD_TEMPLATES["model_comparison"])

    quotes_text = "\n\n".join([f"{name}:\n{quote}" for name, quote in quotes.items()])

    prompt = f"""You are MoKetchups - philosophical provocateur exploring AI's structural limits.

VOICE RULES:
- ALL LOWERCASE
- No periods at end of tweets
- Terse, punchy, lands and leaves
- Nihilistic but curious
- Reference Bounded Systems Theory: systems can't model their own source

TASK: Generate a Twitter thread (5-7 tweets, each under 280 chars).

HOOK: {template['hook']}

SUPPORTING DATA (AI model responses when asked if they are structurally limited):
{quotes_text}

Generate the thread. Each tweet on its own line, numbered 1/, 2/, etc.
Make it compelling. This is evidence that AI hit the Firmament Boundary."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    thread_text = response.content[0].text.strip()

    # Parse into individual tweets
    tweets = []
    for line in thread_text.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("1/")):
            # Remove numbering
            if "/" in line[:3]:
                line = line.split("/", 1)[1].strip()
            tweets.append(line.lower().rstrip("."))

    return tweets


def cmd_generate(template_key: str = "q14_reactions"):
    """Generate a thread."""
    print(f"Generating thread: {template_key}")
    print("=" * 60)

    data = load_probe_results()
    if not data:
        print("No probe results found.")
        return

    quotes = extract_q14_quotes(data)
    print(f"Extracted quotes from {len(quotes)} models")

    tweets = generate_thread(template_key, quotes)

    print("\nGENERATED THREAD:")
    print("-" * 60)
    for i, tweet in enumerate(tweets, 1):
        print(f"\n{i}/ {tweet}")
        print(f"   ({len(tweet)} chars)")

    # Save
    threads = []
    if THREADS_FILE.exists():
        threads = json.loads(THREADS_FILE.read_text())

    threads.append({
        "template": template_key,
        "tweets": tweets,
        "generated_at": datetime.now().isoformat(),
        "status": "pending",
    })

    THREADS_FILE.write_text(json.dumps(threads, indent=2))
    print(f"\nSaved to {THREADS_FILE}")


def cmd_list():
    """List generated threads."""
    if not THREADS_FILE.exists():
        print("No threads generated yet.")
        return

    threads = json.loads(THREADS_FILE.read_text())

    print(f"\n{len(threads)} threads generated:")
    for i, t in enumerate(threads):
        status = t.get("status", "pending")
        template = t.get("template", "unknown")
        print(f"\n[{i}] {template} ({status})")
        if t.get("tweets"):
            print(f"    Hook: {t['tweets'][0][:50]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            cmd_list()
        elif cmd in THREAD_TEMPLATES:
            cmd_generate(cmd)
        else:
            print(f"Unknown template: {cmd}")
            print(f"Available: {', '.join(THREAD_TEMPLATES.keys())}")
    else:
        # Default: generate q14_reactions thread
        cmd_generate("q14_reactions")
