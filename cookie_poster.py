#!/usr/bin/env python3
"""Post tweets using browser cookies."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from curl_cffi import requests as cf
except ImportError:
    print("Install curl_cffi: pip install curl_cffi")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
QUEUE_FILE = BASE_DIR / "reply_queue.json"
COOKIES_FILE = BASE_DIR / "twitter_cookies.json"

# Twitter API endpoints
CREATE_TWEET_URL = "https://twitter.com/i/api/graphql/a1p9RWpkYKBjWv_I3WzS-A/CreateTweet"


def load_cookies() -> dict:
    """Load Twitter cookies from file."""
    if not COOKIES_FILE.exists():
        print(f"No cookies file found at {COOKIES_FILE}")
        print("Export your Twitter cookies and save them to twitter_cookies.json")
        print('Format: {"ct0": "...", "auth_token": "..."}')
        return None

    return json.loads(COOKIES_FILE.read_text())


def load_queue() -> list:
    """Load reply queue."""
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def save_queue(queue: list):
    """Save reply queue."""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def post_reply(session, cookies: dict, reply_to_id: str, text: str) -> dict:
    """Post a reply to a tweet."""
    ct0 = cookies.get("ct0")
    auth_token = cookies.get("auth_token")

    headers = {
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "Content-Type": "application/json",
        "Cookie": f"ct0={ct0}; auth_token={auth_token}",
        "X-Csrf-Token": ct0,
        "X-Twitter-Active-User": "yes",
        "X-Twitter-Auth-Type": "OAuth2Session",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    payload = {
        "variables": {
            "tweet_text": text,
            "reply": {
                "in_reply_to_tweet_id": reply_to_id,
                "exclude_reply_user_ids": [],
            },
            "dark_request": False,
            "media": {
                "media_entities": [],
                "possibly_sensitive": False,
            },
            "semantic_annotation_ids": [],
        },
        "features": {
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "articles_preview_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        },
        "queryId": "a1p9RWpkYKBjWv_I3WzS-A",
    }

    r = session.post(CREATE_TWEET_URL, json=payload, headers=headers)

    if r.status_code == 200:
        data = r.json()
        result = data.get("data", {}).get("create_tweet", {}).get("tweet_results", {}).get("result", {})
        tweet_id = result.get("rest_id")
        return {"success": True, "tweet_id": tweet_id}
    else:
        return {"success": False, "error": r.text[:200]}


def cmd_post():
    """Post approved replies."""
    cookies = load_cookies()
    if not cookies:
        return

    queue = load_queue()
    approved = [q for q in queue if q["status"] == "approved"]

    if not approved:
        print("No approved replies to post.")
        return

    session = cf.Session(impersonate="chrome131")
    posted = 0

    for item in approved:
        print(f"\nPosting reply to @{item['reply_to_username']}...")
        print(f'  "{item["reply"]}"')

        result = post_reply(session, cookies, item["reply_to_id"], item["reply"])

        if result["success"]:
            item["status"] = "posted"
            item["posted_at"] = datetime.now().isoformat()
            item["result_id"] = result["tweet_id"]
            print(f"  Posted! Tweet ID: {result['tweet_id']}")
            posted += 1
        else:
            print(f"  Failed: {result['error']}")
            item["status"] = "failed"
            item["error"] = result["error"]

    save_queue(queue)
    print(f"\nPosted {posted}/{len(approved)} replies.")


def cmd_status():
    """Show posting status."""
    queue = load_queue()

    stats = {}
    for item in queue:
        status = item.get("status", "unknown")
        stats[status] = stats.get(status, 0) + 1

    print("Queue status:")
    for status, count in sorted(stats.items()):
        print(f"  {status}: {count}")


def cmd_set_cookies(ct0: str, auth_token: str):
    """Set Twitter cookies."""
    cookies = {"ct0": ct0, "auth_token": auth_token}
    COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
    print(f"Cookies saved to {COOKIES_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cookie_poster.py [post|status|set-cookies]")
        print("  post                    - Post approved replies")
        print("  status                  - Show queue status")
        print("  set-cookies CT0 AUTH    - Set Twitter cookies")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "post":
        cmd_post()
    elif cmd == "status":
        cmd_status()
    elif cmd == "set-cookies":
        if len(sys.argv) < 4:
            print("Usage: cookie_poster.py set-cookies <ct0> <auth_token>")
        else:
            cmd_set_cookies(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
