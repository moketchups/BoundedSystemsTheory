#!/usr/bin/env python3
"""Real-time Twitter monitor for MoKetchups growth engine."""

import asyncio
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from curl_cffi import requests as cf
except ImportError:
    print("Install curl_cffi: pip install curl_cffi")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Install anthropic: pip install anthropic")
    sys.exit(1)

from config import SEARCH_QUERIES, PRIORITY_ACCOUNTS, MIN_RELEVANCE, MIN_FOLLOWERS, POLL_INTERVAL

BASE_DIR = Path(__file__).parent
SEEN_FILE = BASE_DIR / "realtime_seen.json"
ALERTS_FILE = BASE_DIR / "alerts.json"

# Twitter guest token endpoint
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"


def load_seen() -> set:
    """Load seen tweet IDs."""
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text()))
        except:
            return set()
    return set()


def save_seen(seen: set):
    """Save seen tweet IDs."""
    SEEN_FILE.write_text(json.dumps(list(seen)[-5000:]))  # Keep last 5000


def get_guest_token(session) -> str:
    """Get a Twitter guest token."""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    r = session.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
    if r.status_code == 200:
        return r.json().get("guest_token")
    return None


def search_tweets(session, query: str, guest_token: str) -> list:
    """Search for tweets matching query."""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "x-guest-token": guest_token,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    # Use Twitter's search API
    params = {
        "q": query,
        "result_type": "recent",
        "count": 20,
        "tweet_mode": "extended",
    }

    try:
        r = session.get(
            "https://api.twitter.com/1.1/search/tweets.json",
            params=params,
            headers=headers,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("statuses", [])
    except Exception as e:
        pass

    return []


def calculate_relevance(text: str) -> float:
    """Calculate relevance score based on keywords."""
    text_lower = text.lower()

    high_value = ["consciousness", "sentient", "hallucinate", "alignment", "self-reference", "structural limit"]
    medium_value = ["ai", "llm", "gpt", "claude", "model", "neural", "cognition"]
    low_value = ["think", "understand", "know", "believe", "feel"]

    score = 0.0
    for term in high_value:
        if term in text_lower:
            score += 0.15
    for term in medium_value:
        if term in text_lower:
            score += 0.08
    for term in low_value:
        if term in text_lower:
            score += 0.03

    return min(score, 1.0)


def calculate_intent(text: str) -> tuple:
    """Calculate intent - is this person reaching out / asking questions?"""
    text_lower = text.lower()

    # Reaching indicators
    reaching_patterns = [
        r"\?",  # Questions
        r"why does",
        r"how can",
        r"what if",
        r"anyone",
        r"thoughts on",
        r"controversial",
        r"unpopular opinion",
        r"hot take",
        r"nobody.*talking",
        r"everyone.*talking",
    ]

    score = 0.0
    for pattern in reaching_patterns:
        if re.search(pattern, text_lower):
            score += 0.1

    # Cap at reasonable level
    score = min(score, 0.7)

    return ("reaching", score)


def print_banner():
    """Print startup banner."""
    print("=" * 50)
    print("  MoKetchups Real-Time Monitor")
    print(f"  Polling every ~{POLL_INTERVAL // 60} minutes")
    print(f"  Monitoring {len(SEARCH_QUERIES)} queries")
    print(f"  Priority accounts: {len(PRIORITY_ACCOUNTS)}")
    print("=" * 50)
    print()


async def poll_cycle(session, guest_token: str, seen: set, cycle: int) -> list:
    """Run one polling cycle."""
    now = datetime.now().strftime("%H:%M")

    # Pick random subset of queries to avoid rate limits
    queries = random.sample(SEARCH_QUERIES, min(6, len(SEARCH_QUERIES)))

    print(f"[{now}] Cycle {cycle} - polling {len(queries)} queries...", end=" ", flush=True)

    alerts = []
    new_count = 0

    for query in queries:
        tweets = search_tweets(session, query, guest_token)

        for tweet in tweets:
            tweet_id = tweet.get("id_str")
            if tweet_id in seen:
                continue

            seen.add(tweet_id)
            new_count += 1

            user = tweet.get("user", {})
            followers = user.get("followers_count", 0)
            username = user.get("screen_name", "")
            text = tweet.get("full_text", tweet.get("text", ""))
            likes = tweet.get("favorite_count", 0)
            rts = tweet.get("retweet_count", 0)
            replies = tweet.get("reply_count", 0) if "reply_count" in tweet else 0

            # Skip low follower accounts
            if followers < MIN_FOLLOWERS:
                continue

            relevance = calculate_relevance(text)
            intent_type, intent_score = calculate_intent(text)

            # Check if alert-worthy
            if relevance >= MIN_RELEVANCE:
                alert = {
                    "id": tweet_id,
                    "username": username,
                    "followers": followers,
                    "text": text[:200],
                    "relevance": relevance,
                    "intent": intent_type,
                    "intent_score": intent_score,
                    "likes": likes,
                    "rts": rts,
                    "replies": replies,
                    "found_at": datetime.now().isoformat(),
                }
                alerts.append(alert)

        # Small delay between queries
        await asyncio.sleep(1)

    if new_count > 0:
        print(f"{new_count} new tweets.")
    else:
        print("nothing new.")

    return alerts


def print_alert(alert: dict):
    """Print a single alert."""
    print()
    print("  " + "=" * 50)
    print(f"  ALERT ({alert['intent']}_relevant)")
    print(f"  @{alert['username']} ({alert['followers']} followers)")
    print(f'  "{alert["text"]}"')
    print(f"  Relevance: {alert['relevance']:.3f} | Intent: {alert['intent']} ({alert['intent_score']:.2f})")
    print(f"  Likes: {alert['likes']} | RT: {alert['rts']} | Replies: {alert['replies']}")
    print("  " + "=" * 50)


async def _run_loop():
    """Main monitoring loop."""
    session = cf.Session(impersonate="chrome131")
    seen = load_seen()

    print_banner()

    # Get guest token
    guest_token = get_guest_token(session)
    if not guest_token:
        print("Failed to get guest token. Check network/API status.")
        return

    cycle = 1
    all_alerts = []

    while True:
        try:
            alerts = await poll_cycle(session, guest_token, seen, cycle)

            if alerts:
                for alert in alerts:
                    print_alert(alert)
                    all_alerts.append(alert)

                # Save alerts
                ALERTS_FILE.write_text(json.dumps(all_alerts, indent=2))

                print(f"\n  {len(alerts)} alerts triggered. Run growth_engine.py scan to generate replies.")

            save_seen(seen)

            # Random jitter to avoid detection
            wait_time = POLL_INTERVAL + random.randint(-60, 60)
            print(f"  Next check in ~{wait_time // 60} minutes...")

            await asyncio.sleep(wait_time)
            cycle += 1

            # Refresh guest token periodically
            if cycle % 10 == 0:
                new_token = get_guest_token(session)
                if new_token:
                    guest_token = new_token

        except KeyboardInterrupt:
            print("\nStopping monitor...")
            save_seen(seen)
            break
        except Exception as e:
            print(f"\nError: {e}")
            await asyncio.sleep(60)


def cmd_run():
    """Run the monitor."""
    asyncio.run(_run_loop())


def cmd_status():
    """Show current status."""
    seen = load_seen()
    print(f"Seen tweets: {len(seen)}")

    if ALERTS_FILE.exists():
        alerts = json.loads(ALERTS_FILE.read_text())
        print(f"Pending alerts: {len(alerts)}")
    else:
        print("No alerts yet.")


def cmd_clear():
    """Clear seen cache."""
    if SEEN_FILE.exists():
        SEEN_FILE.unlink()
    print("Cleared seen cache.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python realtime_monitor.py [run|status|clear]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "run":
        cmd_run()
    elif cmd == "status":
        cmd_status()
    elif cmd == "clear":
        cmd_clear()
    else:
        print(f"Unknown command: {cmd}")
