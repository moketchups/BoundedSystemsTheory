#!/usr/bin/env python3
"""
MoKetchups Growth Engine - Unified CLI

Usage:
    moketchups.py scan          - Run smart monitor to find targets
    moketchups.py reply         - Generate replies for top targets
    moketchups.py review        - Review pending replies
    moketchups.py post          - Post approved replies (via cookies)

    moketchups.py tavily        - Scan web for BST-relevant discussions
    moketchups.py thread [type] - Generate a thread from probe data
    moketchups.py post-thread   - Post a generated thread

    moketchups.py probe <model> - Run proof engine on a model
    moketchups.py results       - Show probe results

    moketchups.py status        - Show account and queue status
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


def cmd_scan():
    """Run smart monitor."""
    from smart_monitor import run_smart_scan
    run_smart_scan()


def cmd_reply():
    """Generate replies."""
    from smart_reply import run_smart_reply
    run_smart_reply()


def cmd_review():
    """Review pending replies."""
    from smart_reply import show_replies
    show_replies()


def cmd_post():
    """Post approved replies."""
    from cookie_poster import cmd_post
    cmd_post()


def cmd_tavily():
    """Run Tavily web scanner."""
    from tavily_scanner import scan_web
    scan_web()


def cmd_thread(template: str = "q14_reactions"):
    """Generate a thread."""
    from thread_generator import cmd_generate
    cmd_generate(template)


def cmd_post_thread():
    """Post a generated thread."""
    from content_poster import cmd_post_thread
    cmd_post_thread()


def cmd_probe(model: str):
    """Run proof engine probe."""
    from proof_engine import run_probe
    run_probe(model)


def cmd_results():
    """Show probe results."""
    from proof_engine import cmd_results
    cmd_results([])


def cmd_status():
    """Show overall status."""
    import os
    import requests
    from dotenv import load_dotenv
    from requests_oauthlib import OAuth1
    load_dotenv()

    auth = OAuth1(
        os.getenv("X_CONSUMER_KEY"),
        os.getenv("X_CONSUMER_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_TOKEN_SECRET"),
    )

    # Get account info
    r = requests.get(
        "https://api.twitter.com/2/users/me",
        auth=auth,
        params={"user.fields": "public_metrics"}
    )

    if r.status_code == 200:
        data = r.json()["data"]
        metrics = data.get("public_metrics", {})
        print("=" * 50)
        print(f"  @{data['username']} - {data['name']}")
        print("=" * 50)
        print(f"  Followers: {metrics.get('followers_count', 0):,}")
        print(f"  Following: {metrics.get('following_count', 0):,}")
        print(f"  Tweets: {metrics.get('tweet_count', 0):,}")
        print()

    # Queue status
    alerts_file = BASE_DIR / "smart_alerts.json"
    replies_file = BASE_DIR / "smart_replies.json"
    threads_file = BASE_DIR / "generated_threads.json"

    if alerts_file.exists():
        alerts = json.loads(alerts_file.read_text())
        print(f"  Pending targets: {len(alerts)}")

    if replies_file.exists():
        replies = json.loads(replies_file.read_text())
        print(f"  Generated replies: {len(replies)}")

    if threads_file.exists():
        threads = json.loads(threads_file.read_text())
        pending = [t for t in threads if t.get("status") == "pending"]
        print(f"  Pending threads: {len(pending)}")

    # Probe runs
    probe_dir = BASE_DIR / "probe_runs"
    if probe_dir.exists():
        runs = list(probe_dir.glob("*.json"))
        print(f"  Probe runs: {len(runs)}")


def print_help():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "scan":
            cmd_scan()
        elif cmd == "reply":
            cmd_reply()
        elif cmd == "review":
            cmd_review()
        elif cmd == "post":
            cmd_post()
        elif cmd == "tavily":
            cmd_tavily()
        elif cmd == "thread":
            template = sys.argv[2] if len(sys.argv) > 2 else "q14_reactions"
            cmd_thread(template)
        elif cmd == "post-thread":
            cmd_post_thread()
        elif cmd == "probe":
            if len(sys.argv) < 3:
                print("Specify model: gpt4, claude, gemini, deepseek, grok, all")
            else:
                cmd_probe(sys.argv[2])
        elif cmd == "results":
            cmd_results()
        elif cmd == "status":
            cmd_status()
        elif cmd in ["help", "-h", "--help"]:
            print_help()
        else:
            print(f"Unknown command: {cmd}")
            print_help()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
