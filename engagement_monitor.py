#!/usr/bin/env python3
"""Monitor engagement across platforms."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    from curl_cffi import requests as cf_requests
except ImportError:
    cf_requests = None

load_dotenv()

BASE_DIR = Path(__file__).parent


def check_github():
    """Check GitHub repo stats."""
    url = "https://api.github.com/repos/moketchups/BoundedSystemsTheory"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            "platform": "GitHub",
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("subscribers_count", 0),
            "url": data.get("html_url")
        }
    return {"platform": "GitHub", "error": f"Status {r.status_code}"}


def check_hn(item_id: str = "46759736"):
    """Check HN post stats."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if data:
            return {
                "platform": "HN",
                "title": data.get("title", ""),
                "score": data.get("score", 0),
                "comments": data.get("descendants", 0),
                "url": f"https://news.ycombinator.com/item?id={item_id}"
            }
    return {"platform": "HN", "error": "Not found"}


def check_twitter():
    """Check Twitter stats."""
    bearer = os.getenv("X_BEARER_TOKEN")
    if not bearer:
        return {"platform": "Twitter", "error": "No bearer token"}

    headers = {"Authorization": f"Bearer {bearer}"}

    # Get user info
    r = requests.get(
        "https://api.twitter.com/2/users/by/username/MoKetchups",
        headers=headers,
        params={"user.fields": "public_metrics"}
    )

    if r.status_code == 200:
        data = r.json().get("data", {})
        metrics = data.get("public_metrics", {})
        return {
            "platform": "Twitter",
            "username": data.get("username"),
            "followers": metrics.get("followers_count", 0),
            "following": metrics.get("following_count", 0),
            "tweets": metrics.get("tweet_count", 0),
            "url": "https://x.com/MoKetchups"
        }
    return {"platform": "Twitter", "error": f"Status {r.status_code}"}


def check_medium():
    """Check Medium article stats (limited without auth)."""
    if not cf_requests:
        return {"platform": "Medium", "error": "curl_cffi not installed"}

    session = cf_requests.Session(impersonate="chrome120")
    url = "https://medium.com/@moketchups/the-architecture-of-a-bounded-system-dd1565c0f0eb"

    r = session.get(url)
    if r.status_code == 200:
        # Try to extract claps from page
        html = r.text
        claps_match = re.search(r'"clapCount":(\d+)', html)
        claps = int(claps_match.group(1)) if claps_match else "N/A"

        return {
            "platform": "Medium",
            "title": "The Architecture Of A Bounded System",
            "claps": claps,
            "url": url
        }
    return {"platform": "Medium", "error": f"Status {r.status_code}"}


def check_all():
    """Check all platforms."""
    results = []

    print("Checking GitHub...")
    results.append(check_github())

    print("Checking HN...")
    results.append(check_hn())

    print("Checking Twitter...")
    results.append(check_twitter())

    print("Checking Medium...")
    results.append(check_medium())

    return results


def display_results(results: list):
    """Display results in a nice format."""
    print("\n" + "=" * 60)
    print(f"  ENGAGEMENT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60 + "\n")

    for r in results:
        platform = r.get("platform", "Unknown")
        print(f"  {platform}")
        print("  " + "-" * 30)

        if "error" in r:
            print(f"    Error: {r['error']}")
        else:
            for key, value in r.items():
                if key not in ["platform", "url"]:
                    print(f"    {key}: {value}")
            if "url" in r:
                print(f"    {r['url']}")
        print()


def save_snapshot(results: list):
    """Save engagement snapshot to file."""
    snapshots_dir = BASE_DIR / "engagement_snapshots"
    snapshots_dir.mkdir(exist_ok=True)

    filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = snapshots_dir / filename

    data = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    filepath.write_text(json.dumps(data, indent=2))
    print(f"Snapshot saved: {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: check all and display
        results = check_all()
        display_results(results)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "all":
        results = check_all()
        display_results(results)
    elif cmd == "save":
        results = check_all()
        display_results(results)
        save_snapshot(results)
    elif cmd == "github":
        result = check_github()
        print(json.dumps(result, indent=2))
    elif cmd == "hn":
        item_id = sys.argv[2] if len(sys.argv) > 2 else "46759736"
        result = check_hn(item_id)
        print(json.dumps(result, indent=2))
    elif cmd == "twitter":
        result = check_twitter()
        print(json.dumps(result, indent=2))
    elif cmd == "medium":
        result = check_medium()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: engagement_monitor.py [all|save|github|hn|twitter|medium]")
