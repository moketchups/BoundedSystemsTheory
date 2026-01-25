#!/usr/bin/env python3
"""
Post original content (threads, standalone tweets) to @MoKetchups.
Uses OAuth for authenticated posting.
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
THREADS_FILE = BASE_DIR / "generated_threads.json"
POSTED_FILE = BASE_DIR / "posted_content.json"

# OAuth setup
auth = OAuth1(
    os.getenv("X_CONSUMER_KEY"),
    os.getenv("X_CONSUMER_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_TOKEN_SECRET"),
)


def post_tweet(text: str, reply_to: str = None) -> dict:
    """Post a single tweet."""
    url = "https://api.twitter.com/2/tweets"

    payload = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    r = requests.post(url, auth=auth, json=payload)

    if r.status_code in [200, 201]:
        data = r.json().get("data", {})
        return {"success": True, "id": data.get("id"), "text": data.get("text")}
    else:
        return {"success": False, "error": r.text[:200], "status": r.status_code}


def post_thread(tweets: list) -> list:
    """Post a thread (list of tweets)."""
    results = []
    last_id = None

    for i, tweet in enumerate(tweets):
        print(f"Posting {i+1}/{len(tweets)}: {tweet[:50]}...")

        result = post_tweet(tweet, reply_to=last_id)
        results.append(result)

        if result["success"]:
            last_id = result["id"]
            print(f"  Posted: {result['id']}")
        else:
            print(f"  Failed: {result['error']}")
            break

        # Rate limit protection
        if i < len(tweets) - 1:
            time.sleep(2)

    return results


def cmd_post_thread(thread_index: int = None):
    """Post a generated thread."""
    if not THREADS_FILE.exists():
        print("No threads generated. Run thread_generator.py first.")
        return

    threads = json.loads(THREADS_FILE.read_text())
    pending = [(i, t) for i, t in enumerate(threads) if t.get("status") == "pending"]

    if not pending:
        print("No pending threads to post.")
        return

    if thread_index is not None:
        if thread_index >= len(threads):
            print(f"Invalid index. Max: {len(threads)-1}")
            return
        idx, thread = thread_index, threads[thread_index]
    else:
        idx, thread = pending[0]

    print(f"\nPosting thread [{idx}]: {thread.get('template')}")
    print("=" * 60)

    tweets = thread.get("tweets", [])
    if not tweets:
        print("Empty thread.")
        return

    # Preview
    print("\nTWEETS TO POST:")
    for i, t in enumerate(tweets, 1):
        print(f"  {i}/ {t}")

    print(f"\nPosting {len(tweets)} tweets...")

    results = post_thread(tweets)

    # Update status
    success_count = sum(1 for r in results if r.get("success"))
    threads[idx]["status"] = "posted" if success_count == len(tweets) else "partial"
    threads[idx]["posted_at"] = datetime.now().isoformat()
    threads[idx]["results"] = results

    THREADS_FILE.write_text(json.dumps(threads, indent=2))

    print(f"\nPosted {success_count}/{len(tweets)} tweets")

    # Get thread URL
    if results and results[0].get("success"):
        thread_url = f"https://x.com/MoKetchups/status/{results[0]['id']}"
        print(f"Thread URL: {thread_url}")


def cmd_post_single(text: str):
    """Post a single tweet."""
    if len(text) > 280:
        print(f"Tweet too long: {len(text)} chars (max 280)")
        return

    print(f"Posting: {text}")
    result = post_tweet(text)

    if result["success"]:
        print(f"Posted! ID: {result['id']}")
        print(f"URL: https://x.com/MoKetchups/status/{result['id']}")
    else:
        print(f"Failed: {result['error']}")


def cmd_quote_tweet(tweet_id: str, text: str):
    """Quote tweet another tweet."""
    quote_url = f"https://twitter.com/i/web/status/{tweet_id}"
    full_text = f"{text}\n\n{quote_url}"

    if len(full_text) > 280:
        print(f"Too long: {len(full_text)} chars")
        return

    result = post_tweet(full_text)
    if result["success"]:
        print(f"Quote tweeted! {result['id']}")
    else:
        print(f"Failed: {result['error']}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  content_poster.py thread [index]  - Post a generated thread")
        print("  content_poster.py single 'text'   - Post a single tweet")
        print("  content_poster.py quote ID 'text' - Quote tweet")
        exit(1)

    cmd = sys.argv[1]

    if cmd == "thread":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        cmd_post_thread(idx)
    elif cmd == "single":
        if len(sys.argv) < 3:
            print("Provide tweet text")
        else:
            cmd_post_single(sys.argv[2])
    elif cmd == "quote":
        if len(sys.argv) < 4:
            print("Provide tweet ID and text")
        else:
            cmd_quote_tweet(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
