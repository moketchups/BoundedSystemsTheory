#!/usr/bin/env python3
"""
Follow manager for @MoKetchups.
The account currently follows 0 people - this needs to change.

Strategic following:
1. Thought leaders in AI limits/consciousness
2. People who engage with BST-relevant content
3. Accounts that reply to the priority targets
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import requests
from requests_oauthlib import OAuth1

BASE_DIR = Path(__file__).parent
FOLLOWED_FILE = BASE_DIR / "followed_accounts.json"

# OAuth setup
auth = OAuth1(
    os.getenv("X_CONSUMER_KEY"),
    os.getenv("X_CONSUMER_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_TOKEN_SECRET"),
)

BEARER = os.getenv("X_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {BEARER}"}

# Tier 1: Must follow - AI limits thought leaders
TIER1_ACCOUNTS = [
    "GaryMarcus",       # AI critic, NYU
    "fchollet",         # Keras creator, AI limits
    "emilymbender",     # Linguistics, AI hype critic
    "mmaboris",         # Philosophy of AI
    "melabordeaux",     # Complexity researcher
    "DrMichaelLevin",   # Biological cognition
    "AnilKSeth",        # Consciousness researcher
    "erikhoel",         # Neuroscience, consciousness
    "Plinz",            # Joscha Bach - AI philosophy
    "ReligionProf",     # AI/hallucinations critic
]

# Tier 2: Active in AI discourse
TIER2_ACCOUNTS = [
    "ylecun",           # Meta AI chief
    "sama",             # OpenAI CEO
    "ESYudkowsky",      # AI safety
    "demaboris",        # Tech philosophy
    "BrianRoemmele",    # Voice AI, future tech
    "JeffDean",         # Google AI
    "kaborado",         # AI researcher
    "tegmark",          # MIT, AI safety
    "waitbutwhy",       # Tim Urban, AI explainer
    "TheZvi",           # AI analysis
]


def get_my_user_id():
    """Get authenticated user's ID."""
    r = requests.get("https://api.twitter.com/2/users/me", auth=auth)
    if r.status_code == 200:
        return r.json()["data"]["id"]
    return None


def get_user_id(username: str):
    """Get user ID from username."""
    r = requests.get(
        f"https://api.twitter.com/2/users/by/username/{username}",
        headers=HEADERS,
    )
    if r.status_code == 200:
        return r.json().get("data", {}).get("id")
    return None


def get_following_count():
    """Get current following count."""
    r = requests.get(
        "https://api.twitter.com/2/users/me",
        auth=auth,
        params={"user.fields": "public_metrics"}
    )
    if r.status_code == 200:
        return r.json()["data"]["public_metrics"]["following_count"]
    return 0


def follow_user(my_id: str, target_id: str):
    """Follow a user."""
    r = requests.post(
        f"https://api.twitter.com/2/users/{my_id}/following",
        auth=auth,
        json={"target_user_id": target_id},
    )

    if r.status_code == 200:
        result = r.json().get("data", {})
        if result.get("following"):
            return "followed"
        elif result.get("pending_follow"):
            return "pending"
    elif r.status_code == 403:
        return "blocked_or_protected"
    elif r.status_code == 429:
        return "rate_limited"

    return f"error:{r.status_code}"


def load_followed():
    """Load list of followed accounts."""
    if FOLLOWED_FILE.exists():
        return json.loads(FOLLOWED_FILE.read_text())
    return {"followed": [], "failed": []}


def save_followed(data):
    """Save followed accounts list."""
    FOLLOWED_FILE.write_text(json.dumps(data, indent=2))


def cmd_follow_tier1():
    """Follow all Tier 1 accounts."""
    my_id = get_my_user_id()
    if not my_id:
        print("Auth failed")
        return

    followed_data = load_followed()
    already_followed = set(followed_data.get("followed", []))

    print(f"Following Tier 1 accounts...")
    print(f"Currently following: {get_following_count()}")
    print("=" * 50)

    for username in TIER1_ACCOUNTS:
        if username.lower() in [x.lower() for x in already_followed]:
            print(f"  @{username}: already followed")
            continue

        target_id = get_user_id(username)
        if not target_id:
            print(f"  @{username}: not found")
            continue

        result = follow_user(my_id, target_id)
        print(f"  @{username}: {result}")

        if result in ["followed", "pending"]:
            followed_data["followed"].append(username)
        else:
            followed_data["failed"].append({"username": username, "reason": result})

        time.sleep(1)  # Rate limit

    save_followed(followed_data)
    print(f"\nNow following: {get_following_count()}")


def cmd_follow_tier2():
    """Follow Tier 2 accounts."""
    my_id = get_my_user_id()
    if not my_id:
        print("Auth failed")
        return

    followed_data = load_followed()
    already_followed = set(followed_data.get("followed", []))

    print(f"Following Tier 2 accounts...")
    print("=" * 50)

    for username in TIER2_ACCOUNTS:
        if username.lower() in [x.lower() for x in already_followed]:
            print(f"  @{username}: already followed")
            continue

        target_id = get_user_id(username)
        if not target_id:
            print(f"  @{username}: not found")
            continue

        result = follow_user(my_id, target_id)
        print(f"  @{username}: {result}")

        if result in ["followed", "pending"]:
            followed_data["followed"].append(username)

        time.sleep(1)

    save_followed(followed_data)
    print(f"\nNow following: {get_following_count()}")


def cmd_status():
    """Show following status."""
    count = get_following_count()
    followed_data = load_followed()

    print(f"Following count: {count}")
    print(f"Tracked follows: {len(followed_data.get('followed', []))}")
    print(f"Failed follows: {len(followed_data.get('failed', []))}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  follow_manager.py tier1   - Follow Tier 1 (thought leaders)")
        print("  follow_manager.py tier2   - Follow Tier 2 (AI discourse)")
        print("  follow_manager.py status  - Show following status")
        exit(1)

    cmd = sys.argv[1]

    if cmd == "tier1":
        cmd_follow_tier1()
    elif cmd == "tier2":
        cmd_follow_tier2()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown: {cmd}")
