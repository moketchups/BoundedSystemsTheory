#!/usr/bin/env python3
"""Cross-post content to multiple platforms at once."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Import posters
try:
    from reddit_poster import post_bst_text as reddit_post
except ImportError:
    reddit_post = None

try:
    from devto_poster import post_bst_article as devto_post
except ImportError:
    devto_post = None

try:
    from hn_poster import post_bst as hn_post
except ImportError:
    hn_post = None

try:
    from medium_poster import create_draft as medium_draft
except ImportError:
    medium_draft = None


def cross_post_all(publish: bool = False):
    """Post to all available platforms."""
    results = {}

    print("=" * 50)
    print("  CROSS-POSTING BST")
    print("=" * 50)

    # HN
    print("\n[HN] Posting...")
    if hn_post:
        try:
            result = hn_post()
            results["hn"] = result
            if result.get("success"):
                print(f"  SUCCESS: {result['url']}")
            else:
                print(f"  FAILED: {result.get('error')}")
        except Exception as e:
            results["hn"] = {"success": False, "error": str(e)}
            print(f"  ERROR: {e}")
    else:
        print("  SKIPPED: hn_poster not available")

    # Reddit
    print("\n[Reddit] Posting...")
    if reddit_post:
        try:
            result = reddit_post("artificial")
            results["reddit"] = result
            if result:
                print(f"  SUCCESS: {result.get('url')}")
            else:
                print("  FAILED: No result")
        except Exception as e:
            results["reddit"] = {"success": False, "error": str(e)}
            print(f"  ERROR: {e}")
    else:
        print("  SKIPPED: reddit_poster not available")

    # Dev.to
    print("\n[Dev.to] Posting...")
    if devto_post:
        try:
            result = devto_post(published=publish)
            results["devto"] = result
            if result and result.get("success"):
                print(f"  SUCCESS: {result['url']}")
            else:
                print(f"  FAILED: {result}")
        except Exception as e:
            results["devto"] = {"success": False, "error": str(e)}
            print(f"  ERROR: {e}")
    else:
        print("  SKIPPED: devto_poster not available")

    # Medium
    print("\n[Medium] Creating draft...")
    if medium_draft:
        try:
            result = medium_draft()
            results["medium"] = result
            if result:
                print(f"  SUCCESS: Draft at {result.get('edit_url')}")
            else:
                print("  FAILED: No result")
        except Exception as e:
            results["medium"] = {"success": False, "error": str(e)}
            print(f"  ERROR: {e}")
    else:
        print("  SKIPPED: medium_poster not available")

    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)

    for platform, result in results.items():
        status = "OK" if result and result.get("success", result.get("url")) else "FAIL"
        print(f"  {platform}: {status}")

    return results


def cross_post_drafts():
    """Create drafts on all platforms (no publishing)."""
    return cross_post_all(publish=False)


def cross_post_publish():
    """Publish to all platforms."""
    return cross_post_all(publish=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cross_post.py [draft|publish]")
        print("  draft   - Create drafts on all platforms")
        print("  publish - Publish to all platforms")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "draft":
        cross_post_drafts()
    elif cmd == "publish":
        cross_post_publish()
    else:
        print(f"Unknown command: {cmd}")
