#!/usr/bin/env python3
"""Post to Hacker News using Playwright automation."""

import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent


def login(page, username: str, password: str) -> bool:
    """Login to HN."""
    page.goto("https://news.ycombinator.com/login")
    time.sleep(2)

    # Find create account form (has hidden creating=t input)
    create_form = page.query_selector('form:has(input[name="creating"])')

    if create_form:
        # Account doesn't exist, create it
        create_form.query_selector('input[name="acct"]').fill(username)
        create_form.query_selector('input[name="pw"]').fill(password)
        create_form.query_selector('input[type="submit"]').click()
        time.sleep(3)

        if "logout" in page.content().lower():
            print(f"Account '{username}' created and logged in")
            return True

    # Try regular login
    page.fill('input[name="acct"]', username)
    page.fill('input[name="pw"]', password)
    page.click('input[type="submit"]')
    time.sleep(3)

    return "logout" in page.content().lower()


def post_link(username: str, password: str, title: str, url: str) -> dict:
    """Post a link to HN."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        if not login(page, username, password):
            browser.close()
            return {"success": False, "error": "Login failed"}

        # Go to submit page
        page.goto("https://news.ycombinator.com/submit")
        time.sleep(2)

        # Fill form
        page.fill('input[name="title"]', title)
        page.fill('input[name="url"]', url)
        page.click('input[type="submit"]')
        time.sleep(3)

        result_url = page.url

        # Check for errors
        if "toolong" in result_url.lower():
            browser.close()
            return {"success": False, "error": "Title too long"}

        if "item?id=" in result_url:
            browser.close()
            return {"success": True, "url": result_url}

        # Check submitted page
        page.goto(f"https://news.ycombinator.com/submitted?id={username}")
        time.sleep(2)

        # Find the post link
        links = page.query_selector_all('a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.startswith('item?id='):
                post_url = f"https://news.ycombinator.com/{href}"
                browser.close()
                return {"success": True, "url": post_url}

        browser.close()
        return {"success": False, "error": "Could not find posted item"}


def post_text(username: str, password: str, title: str, text: str) -> dict:
    """Post a text post to HN."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        if not login(page, username, password):
            browser.close()
            return {"success": False, "error": "Login failed"}

        page.goto("https://news.ycombinator.com/submit")
        time.sleep(2)

        page.fill('input[name="title"]', title)
        page.fill('textarea[name="text"]', text)
        page.click('input[type="submit"]')
        time.sleep(3)

        result_url = page.url
        browser.close()

        if "item?id=" in result_url:
            return {"success": True, "url": result_url}
        return {"success": False, "error": "Post may have failed", "url": result_url}


def post_bst():
    """Post BST to HN."""
    username = os.getenv("HN_USERNAME", "BoundedSystems")
    password = os.getenv("HN_PASSWORD", "LilyRosepZaVno96!")

    title = "Show HN: 5 AIs read an article about their structural limits"
    url = "https://github.com/moketchups/BoundedSystemsTheory"

    return post_link(username, password, title, url)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hn_poster.py [test|post|text]")
        print("  test           - Test HN login")
        print("  post           - Post BST GitHub link")
        print("  link <t> <url> - Post custom link")
        print("  text <t> <txt> - Post custom text")
        print("")
        print("Set HN_USERNAME and HN_PASSWORD in .env, or uses defaults")
        sys.exit(1)

    cmd = sys.argv[1]
    username = os.getenv("HN_USERNAME", "BoundedSystems")
    password = os.getenv("HN_PASSWORD", "LilyRosepZaVno96!")

    if cmd == "test":
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            if login(page, username, password):
                print(f"Logged in as: {username}")
            else:
                print("Login failed")
            browser.close()

    elif cmd == "post":
        result = post_bst()
        if result["success"]:
            print(f"Posted: {result['url']}")
        else:
            print(f"Failed: {result['error']}")

    elif cmd == "link" and len(sys.argv) >= 4:
        title = sys.argv[2]
        url = sys.argv[3]
        result = post_link(username, password, title, url)
        if result["success"]:
            print(f"Posted: {result['url']}")
        else:
            print(f"Failed: {result}")

    elif cmd == "text" and len(sys.argv) >= 4:
        title = sys.argv[2]
        text = sys.argv[3]
        result = post_text(username, password, title, text)
        if result["success"]:
            print(f"Posted: {result['url']}")
        else:
            print(f"Failed: {result}")

    else:
        print(f"Unknown command or missing args: {cmd}")
