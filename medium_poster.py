#!/usr/bin/env python3
"""Post to Medium using cookies."""

import json
import os
import sys
from pathlib import Path

try:
    from curl_cffi import requests
except ImportError:
    print("Install curl_cffi: pip install curl_cffi")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent


def get_session():
    """Get authenticated Medium session."""
    sid = os.getenv("MEDIUM_SID")
    uid = os.getenv("MEDIUM_UID")

    if not sid or not uid:
        print("Missing Medium credentials in .env")
        print("Required: MEDIUM_SID, MEDIUM_UID")
        return None, None

    cookies = {"sid": sid, "uid": uid}
    session = requests.Session(impersonate="chrome120")

    # Get XSRF token
    r = session.get("https://medium.com/new-story", cookies=cookies)
    xsrf = r.cookies.get("xsrf")
    cookies["xsrf"] = xsrf

    return session, cookies


def get_user_info():
    """Get current user info."""
    session, cookies = get_session()
    if not session:
        return None

    r = session.get("https://medium.com/me", cookies=cookies)
    return {"url": r.url, "status": r.status_code}


def create_draft():
    """Create a new empty draft and return its ID."""
    session, cookies = get_session()
    if not session:
        return None

    xsrf = cookies.get("xsrf")
    headers = {
        "Content-Type": "application/json",
        "x-xsrf-token": xsrf,
    }

    mutation = {
        "operationName": "CreatePostMutation",
        "variables": {"input": {}},
        "query": """
            mutation CreatePostMutation($input: CreatePostInput!) {
                createPost(input: $input) {
                    id
                    mediumUrl
                    title
                }
            }
        """
    }

    r = session.post(
        "https://medium.com/_/graphql",
        cookies=cookies,
        headers=headers,
        json=mutation
    )

    text = r.text
    if text.startswith(")]}'"):
        text = text[5:]

    data = json.loads(text)
    post_data = data.get("data", {}).get("createPost", {})

    return {
        "id": post_data.get("id"),
        "url": post_data.get("mediumUrl"),
        "edit_url": f"https://medium.com/p/{post_data.get('id')}/edit"
    }


def list_drafts():
    """List user's drafts."""
    session, cookies = get_session()
    if not session:
        return None

    # Get user profile to find drafts
    r = session.get("https://medium.com/me/stories/drafts", cookies=cookies)
    return {"status": r.status_code, "url": r.url}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python medium_poster.py [test|draft|drafts]")
        print("  test    - Test Medium connection")
        print("  draft   - Create new draft (returns edit URL)")
        print("  drafts  - List drafts")
        print("")
        print("Note: Medium's API is limited. For full articles, create a draft")
        print("and edit it manually at the returned URL.")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        info = get_user_info()
        if info:
            print(f"Logged in: {info['url']}")
    elif cmd == "draft":
        result = create_draft()
        if result:
            print(f"Draft created!")
            print(f"  ID: {result['id']}")
            print(f"  Edit URL: {result['edit_url']}")
    elif cmd == "drafts":
        result = list_drafts()
        if result:
            print(f"Drafts page: {result['url']}")
    else:
        print(f"Unknown command: {cmd}")
