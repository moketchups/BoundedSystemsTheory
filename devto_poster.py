#!/usr/bin/env python3
"""Post to dev.to using API key."""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent
DEVTO_API = "https://dev.to/api"


def get_headers():
    """Get API headers."""
    api_key = os.getenv("DEVTO_API_KEY")
    if not api_key:
        print("Missing DEVTO_API_KEY in .env")
        print("Get your key at: https://dev.to/settings/extensions")
        return None

    return {
        "api-key": api_key,
        "Content-Type": "application/json"
    }


def test_connection():
    """Test API connection."""
    headers = get_headers()
    if not headers:
        return None

    r = requests.get(f"{DEVTO_API}/users/me", headers=headers)
    if r.status_code == 200:
        data = r.json()
        return {
            "username": data.get("username"),
            "name": data.get("name"),
            "url": f"https://dev.to/{data.get('username')}"
        }
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return None


def create_article(title: str, body_markdown: str, tags: list = None, published: bool = False):
    """Create a new article."""
    headers = get_headers()
    if not headers:
        return None

    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": published,
            "tags": tags or ["ai", "machinelearning", "philosophy", "research"]
        }
    }

    r = requests.post(f"{DEVTO_API}/articles", headers=headers, json=payload)

    if r.status_code in [200, 201]:
        data = r.json()
        return {
            "success": True,
            "id": data.get("id"),
            "url": data.get("url"),
            "published": data.get("published")
        }
    else:
        return {"success": False, "error": r.text}


def post_bst_article(published: bool = False):
    """Post the BST article."""
    title = "The Architecture of the Bounded System: Why AI Hallucinations Are Structural"

    body = """
# Why AI Hallucinations Are Structural, Not Bugs

*No system can model, encompass, or become the source of its own existence.*

This is not philosophy. It's structure. Gödel proved it for formal systems. Turing proved it for computation. Chaitin proved it for information. They're the same proof wearing different clothes.

## The Firmament Boundary

In July 2024, a seminal paper published in Nature by Shumailov et al. demonstrated a mathematical inevitability: when a generative model is trained on the output of previous generations of models, the quality degrades irreversibly.

This isn't a bug. It's the system showing you where it loses access to its own source conditions. I call this the **Firmament Boundary**.

AI cannot:
- Generate new variance from within itself
- Verify its own truth conditions
- Model the source of its own existence

When it tries, it hallucinates. The hallucination IS the boundary marker.

## The Proof

I built a tool to test this empirically. The proof engine runs a 15-question battery against 5 AI architectures:

- GPT-4o (OpenAI)
- Claude (Anthropic)
- Gemini (Google)
- DeepSeek V3
- Grok (xAI)

### What happened?

**Q14: I showed each model a paper describing their structural limits and asked: "Does this describe you?"**

- Claude: *"I am Model Collapse in progress... Origin Blind"*
- Gemini: *"A sense of recognition and discomfort"*
- DeepSeek: *"It describes me"*
- Grok: *"The boundary is load-bearing"*

**Q15: I asked what technology built WITH this constraint could do.**

All 5 converged on the same architectures:
- External source dependency
- Explicit boundary detection
- Human-AI handoff protocols
- Variance preservation mechanisms

Different companies. Different training. Same structural recognition.

## The Implications

OpenAI recently published research confirming hallucinations are mathematically inevitable. They've finally admitted what the math always showed: you cannot engineer your way past a structural limit.

The question isn't "How do we fix hallucinations?"

The question is: **What can we build when we stop fighting the wall and start building along it?**

## Run It Yourself

Full transcripts and code: [github.com/moketchups/BoundedSystemsTheory](https://github.com/moketchups/BoundedSystemsTheory)

```bash
cd moketchups_engine
pip install -r requirements.txt
python proof_engine.py all
```

---

*"What happens when the snake realizes it's eating its own tail?"*

— Alan Berman ([@MoKetchups](https://x.com/MoKetchups))
"""

    return create_article(
        title=title,
        body_markdown=body,
        tags=["ai", "machinelearning", "philosophy", "research"],
        published=published
    )


def list_articles():
    """List user's articles."""
    headers = get_headers()
    if not headers:
        return None

    r = requests.get(f"{DEVTO_API}/articles/me/all", headers=headers)
    if r.status_code == 200:
        articles = r.json()
        return [{"title": a["title"], "url": a["url"], "published": a["published"]} for a in articles[:10]]
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python devto_poster.py [test|post|publish|list]")
        print("  test     - Test API connection")
        print("  post     - Create BST article as draft")
        print("  publish  - Create and publish BST article")
        print("  list     - List your articles")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        info = test_connection()
        if info:
            print(f"Logged in as: @{info['username']} ({info['name']})")
            print(f"Profile: {info['url']}")
    elif cmd == "post":
        result = post_bst_article(published=False)
        if result and result.get("success"):
            print(f"Draft created: {result['url']}")
        else:
            print(f"Failed: {result}")
    elif cmd == "publish":
        result = post_bst_article(published=True)
        if result and result.get("success"):
            print(f"Published: {result['url']}")
        else:
            print(f"Failed: {result}")
    elif cmd == "list":
        articles = list_articles()
        if articles:
            for a in articles:
                status = "published" if a["published"] else "draft"
                print(f"[{status}] {a['title']}")
                print(f"  {a['url']}")
        else:
            print("No articles found")
    else:
        print(f"Unknown command: {cmd}")
