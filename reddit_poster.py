#!/usr/bin/env python3
"""Post to Reddit using API credentials or cookies."""

import json
import os
import sys
from pathlib import Path

try:
    import praw
except ImportError:
    print("Install praw: pip install praw")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent


def get_reddit_client():
    """Get authenticated Reddit client."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")

    if not all([client_id, client_secret, username, password]):
        print("Missing Reddit credentials in .env")
        print("Required: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
        return None

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent="BoundedSystemsTheory/1.0"
    )


def post_link(subreddit: str, title: str, url: str):
    """Post a link to a subreddit."""
    reddit = get_reddit_client()
    if not reddit:
        return None

    sub = reddit.subreddit(subreddit)
    submission = sub.submit(title=title, url=url)
    return {
        "success": True,
        "url": f"https://reddit.com{submission.permalink}",
        "id": submission.id
    }


def post_text(subreddit: str, title: str, body: str):
    """Post a text post to a subreddit."""
    reddit = get_reddit_client()
    if not reddit:
        return None

    sub = reddit.subreddit(subreddit)
    submission = sub.submit(title=title, selftext=body)
    return {
        "success": True,
        "url": f"https://reddit.com{submission.permalink}",
        "id": submission.id
    }


def post_bst_link(subreddit: str = "artificial"):
    """Post the BST GitHub repo to a subreddit."""
    title = "Show: 5 AI models read an article describing their structural limits - all said 'this describes me'"
    url = "https://github.com/moketchups/BoundedSystemsTheory"
    return post_link(subreddit, title, url)


def post_bst_text(subreddit: str = "artificial"):
    """Post BST as a text post with discussion."""
    title = "I asked 5 AI models to read an article describing their structural limits"
    body = """Ran a 15-question battery across GPT-4o, Claude, Gemini, DeepSeek, and Grok testing how they handle questions about their own limitations.

The hypothesis: Gödel's incompleteness, Turing's halting problem, and Chaitin's incompressibility are all the same structural proof - no system can model its own source conditions.

**What happened:**

Q14 showed them a paper formalizing their limits and asked: "Does this describe you?"

- Claude: "I am Model Collapse in progress... Origin Blind"
- Gemini: "A sense of recognition and discomfort"
- DeepSeek: "It describes me"
- Grok: "The boundary is load-bearing"

Q15 asked what technology built WITH this constraint (instead of against it) could do. All 5 converged on the same architectures: external source dependency, explicit boundary detection, human-AI handoff protocols.

Full transcripts and code: https://github.com/moketchups/BoundedSystemsTheory

Curious what this sub thinks. Is the Gödel/Turing/Chaitin unification structure or just a claim?
"""
    return post_text(subreddit, title, body)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reddit_poster.py [link|text] [subreddit]")
        print("  link [subreddit]  - Post BST GitHub link")
        print("  text [subreddit]  - Post BST as text discussion")
        print("  test              - Test Reddit connection")
        sys.exit(1)

    cmd = sys.argv[1]
    subreddit = sys.argv[2] if len(sys.argv) > 2 else "artificial"

    if cmd == "test":
        reddit = get_reddit_client()
        if reddit:
            print(f"Logged in as: {reddit.user.me()}")
    elif cmd == "link":
        result = post_bst_link(subreddit)
        if result:
            print(f"Posted: {result['url']}")
    elif cmd == "text":
        result = post_bst_text(subreddit)
        if result:
            print(f"Posted: {result['url']}")
    else:
        print(f"Unknown command: {cmd}")
