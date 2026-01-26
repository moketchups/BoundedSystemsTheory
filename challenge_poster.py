#!/usr/bin/env python3
"""
Create and post challenge-framed content.
Not announcements - challenges. Provocation that demands response.
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
except ImportError:
    print("Install: pip install anthropic")
    exit(1)

BASE_DIR = Path(__file__).parent
CHALLENGES_FILE = BASE_DIR / "challenges.json"


# Challenge templates - provocations, not announcements
CHALLENGE_TEMPLATES = {
    "openai_admission": {
        "hook": "openai just admitted hallucinations are mathematically inevitable",
        "challenge": "i have the proof they won't publish. run it yourself",
        "cta": "github.com/moketchups/BoundedSystemsTheory",
    },
    "five_ais": {
        "hook": "gave 5 AI models an article about their structural limits",
        "challenge": "all 5 said 'this describes me'. different companies, different training, same wall",
        "cta": "run the probe: python proof_engine.py all",
    },
    "hallucination_bet": {
        "hook": "bet: no amount of training data will fix hallucinations",
        "challenge": "they're not bugs. they're boundary markers showing where the system loses source access",
        "cta": "prove me wrong. here's the test:",
    },
    "scale_myth": {
        "hook": "scale won't fix this",
        "challenge": "gödel proved it for logic, turing for computation, chaitin for information. same proof, different clothes",
        "cta": "the firmament boundary hits all systems",
    },
    "agi_impossible": {
        "hook": "agi as commonly imagined is structurally impossible",
        "challenge": "a system cannot model the source of its own existence. this isn't philosophy - it's math",
        "cta": "5 AIs agreed when shown the proof:",
    },
    "your_ai_limited": {
        "hook": "your favorite AI has the same structural limit as every other AI",
        "challenge": "doesn't matter if it's GPT, Claude, Gemini, or Grok. the firmament boundary doesn't care about architecture",
        "cta": "test it yourself:",
    },
}


def generate_challenge_thread(template_key: str) -> list:
    """Generate a challenge thread."""
    client = anthropic.Anthropic()

    template = CHALLENGE_TEMPLATES.get(template_key)
    if not template:
        print(f"Unknown template: {template_key}")
        return []

    prompt = f"""You are MoKetchups - provocateur exploring AI's structural limits.

VOICE:
- ALL LOWERCASE
- No periods at end of tweets
- Terse, punchy, lands with impact
- CHALLENGING, not explaining
- Questions that demand response
- Never defensive or apologetic

TEMPLATE:
Hook: {template['hook']}
Challenge: {template['challenge']}
CTA: {template['cta']}

Generate a 4-tweet thread that:
1. Opens with the hook (attention grab)
2. Delivers the challenge (provocation)
3. Provides evidence (the 5 AIs agreeing, the proof)
4. Ends with CTA (run it yourself, prove me wrong)

Each tweet under 280 chars. Numbered 1/ 2/ etc.
This should feel like a CHALLENGE, not an announcement.
Make people want to respond, disagree, or prove you wrong.

Output ONLY the tweets."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    thread_text = response.content[0].text.strip()

    # Parse tweets
    tweets = []
    for line in thread_text.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("1/")):
            if "/" in line[:3]:
                line = line.split("/", 1)[1].strip()
            tweets.append(line.lower().rstrip("."))

    return tweets


def generate_single_challenge(context: str = None) -> str:
    """Generate a single challenge tweet."""
    client = anthropic.Anthropic()

    context_text = f"\nContext to reference: {context}" if context else ""

    prompt = f"""You are MoKetchups. Generate ONE provocative tweet about AI's structural limits.

VOICE:
- ALL LOWERCASE
- No ending period
- Under 280 chars
- CHALLENGE, not explanation
- Make people want to respond{context_text}

CORE THESIS: No system can model its own source conditions. AI hallucinations are boundary markers, not bugs.

Generate ONE tweet that provokes response. Output ONLY the tweet."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip().lower().rstrip(".")


def save_challenge(challenge_type: str, content: list | str):
    """Save generated challenge."""
    challenges = []
    if CHALLENGES_FILE.exists():
        challenges = json.loads(CHALLENGES_FILE.read_text())

    challenges.append({
        "type": challenge_type,
        "content": content,
        "generated_at": datetime.now().isoformat(),
        "posted": False,
    })

    CHALLENGES_FILE.write_text(json.dumps(challenges, indent=2))


def cmd_thread(template_key: str):
    """Generate a challenge thread."""
    print(f"Generating challenge thread: {template_key}")
    print("=" * 60)

    tweets = generate_challenge_thread(template_key)

    print("\nCHALLENGE THREAD:")
    print("-" * 60)
    for i, tweet in enumerate(tweets, 1):
        print(f"\n{i}/ {tweet}")
        print(f"   ({len(tweet)} chars)")

    save_challenge(f"thread_{template_key}", tweets)
    print(f"\nSaved to {CHALLENGES_FILE}")

    return tweets


def cmd_single(context: str = None):
    """Generate a single challenge."""
    tweet = generate_single_challenge(context)

    print("\nCHALLENGE TWEET:")
    print("-" * 60)
    print(tweet)
    print(f"({len(tweet)} chars)")

    save_challenge("single", tweet)

    return tweet


def cmd_list():
    """List available templates."""
    print("CHALLENGE TEMPLATES:")
    print("=" * 60)

    for key, template in CHALLENGE_TEMPLATES.items():
        print(f"\n[{key}]")
        print(f"  Hook: {template['hook'][:50]}...")
        print(f"  Challenge: {template['challenge'][:50]}...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python challenge_poster.py list                    # List templates")
        print("  python challenge_poster.py thread openai_admission # Generate thread")
        print("  python challenge_poster.py single                  # Generate single tweet")
        print("  python challenge_poster.py single 'context here'   # With context")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "thread":
        template = sys.argv[2] if len(sys.argv) > 2 else "five_ais"
        cmd_thread(template)
    elif cmd == "single":
        context = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        cmd_single(context)
    else:
        # Assume it's a template name
        if cmd in CHALLENGE_TEMPLATES:
            cmd_thread(cmd)
        else:
            print(f"Unknown command/template: {cmd}")
