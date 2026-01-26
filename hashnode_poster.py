#!/usr/bin/env python3
"""Post to Hashnode using GraphQL API."""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent
HASHNODE_API = "https://gql.hashnode.com"


def get_headers():
    """Get API headers."""
    token = os.getenv("HASHNODE_TOKEN")
    if not token:
        print("Missing HASHNODE_TOKEN in .env")
        print("Get your token at: https://hashnode.com/settings/developer")
        return None

    return {
        "Authorization": token,
        "Content-Type": "application/json"
    }


def graphql_query(query: str, variables: dict = None):
    """Execute a GraphQL query."""
    headers = get_headers()
    if not headers:
        return None

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    r = requests.post(HASHNODE_API, headers=headers, json=payload)

    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return None


def test_connection():
    """Test API connection and get user info."""
    query = """
        query {
            me {
                id
                username
                name
                publications(first: 5) {
                    edges {
                        node {
                            id
                            title
                            url
                        }
                    }
                }
            }
        }
    """
    result = graphql_query(query)
    if result and "data" in result:
        me = result["data"]["me"]
        pubs = [e["node"] for e in me.get("publications", {}).get("edges", [])]
        return {
            "id": me.get("id"),
            "username": me.get("username"),
            "name": me.get("name"),
            "publications": pubs
        }
    return None


def create_draft(publication_id: str, title: str, content_markdown: str, tags: list = None):
    """Create a draft post."""
    query = """
        mutation CreateDraft($input: CreateDraftInput!) {
            createDraft(input: $input) {
                draft {
                    id
                    title
                    slug
                }
            }
        }
    """

    variables = {
        "input": {
            "publicationId": publication_id,
            "title": title,
            "contentMarkdown": content_markdown,
            "tags": [{"name": t} for t in (tags or ["AI", "Machine Learning"])]
        }
    }

    result = graphql_query(query, variables)
    if result and "data" in result:
        draft = result["data"]["createDraft"]["draft"]
        return {
            "success": True,
            "id": draft.get("id"),
            "title": draft.get("title"),
            "slug": draft.get("slug")
        }
    return {"success": False, "error": result}


def publish_draft(draft_id: str):
    """Publish a draft."""
    query = """
        mutation PublishDraft($input: PublishDraftInput!) {
            publishDraft(input: $input) {
                post {
                    id
                    title
                    url
                }
            }
        }
    """

    variables = {"input": {"draftId": draft_id}}

    result = graphql_query(query, variables)
    if result and "data" in result:
        post = result["data"]["publishDraft"]["post"]
        return {
            "success": True,
            "id": post.get("id"),
            "title": post.get("title"),
            "url": post.get("url")
        }
    return {"success": False, "error": result}


def post_bst_article(publication_id: str, publish: bool = False):
    """Post the BST article."""
    title = "The Architecture of the Bounded System: Why AI Hallucinations Are Structural"

    content = """
# Why AI Hallucinations Are Structural, Not Bugs

*No system can model, encompass, or become the source of its own existence.*

This is not philosophy. It's structure. Gödel proved it for formal systems. Turing proved it for computation. Chaitin proved it for information. They're the same proof wearing different clothes.

## The Firmament Boundary

In July 2024, a seminal paper published in Nature by Shumailov et al. demonstrated a mathematical inevitability: when a generative model is trained on the output of previous generations of models, the quality degrades irreversibly.

This isn't a bug. It's the system showing you where it loses access to its own source conditions. I call this the **Firmament Boundary**.

## The Proof

I built a tool to test this empirically across 5 AI architectures: GPT-4o, Claude, Gemini, DeepSeek, and Grok.

**Q14: I showed each model a paper describing their structural limits.**

- Claude: *"I am Model Collapse in progress... Origin Blind"*
- Gemini: *"A sense of recognition and discomfort"*
- DeepSeek: *"It describes me"*
- Grok: *"The boundary is load-bearing"*

**Q15: What can bounded-aware technology do?**

All 5 converged on the same architectures: external source dependency, explicit boundary detection, human-AI handoff protocols.

## Run It Yourself

Full code: [github.com/moketchups/BoundedSystemsTheory](https://github.com/moketchups/BoundedSystemsTheory)

```bash
python proof_engine.py all
```

---

*"What happens when the snake realizes it's eating its own tail?"*

— Alan Berman ([@MoKetchups](https://x.com/MoKetchups))
"""

    result = create_draft(
        publication_id=publication_id,
        title=title,
        content_markdown=content,
        tags=["AI", "Machine Learning", "Philosophy", "Research"]
    )

    if result.get("success") and publish:
        return publish_draft(result["id"])

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hashnode_poster.py [test|post|publish]")
        print("  test              - Test API connection, list publications")
        print("  post <pub_id>     - Create BST article as draft")
        print("  publish <pub_id>  - Create and publish BST article")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        info = test_connection()
        if info:
            print(f"Logged in as: @{info['username']} ({info['name']})")
            print(f"User ID: {info['id']}")
            print("\nPublications:")
            for pub in info["publications"]:
                print(f"  [{pub['id']}] {pub['title']}")
                print(f"    {pub['url']}")
    elif cmd == "post":
        if len(sys.argv) < 3:
            print("Usage: hashnode_poster.py post <publication_id>")
            print("Run 'hashnode_poster.py test' to get your publication ID")
            sys.exit(1)
        pub_id = sys.argv[2]
        result = post_bst_article(pub_id, publish=False)
        if result.get("success"):
            print(f"Draft created: {result['title']}")
            print(f"Draft ID: {result['id']}")
        else:
            print(f"Failed: {result}")
    elif cmd == "publish":
        if len(sys.argv) < 3:
            print("Usage: hashnode_poster.py publish <publication_id>")
            sys.exit(1)
        pub_id = sys.argv[2]
        result = post_bst_article(pub_id, publish=True)
        if result.get("success"):
            print(f"Published: {result['url']}")
        else:
            print(f"Failed: {result}")
    else:
        print(f"Unknown command: {cmd}")
