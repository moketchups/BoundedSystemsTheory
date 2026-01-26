#!/usr/bin/env python3
"""Format articles for different platforms."""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent


# The core BST article content
BST_ARTICLE = {
    "title": "The Architecture of the Bounded System",
    "subtitle": "Why AI Hallucinations Are Structural, Not Bugs",
    "author": "Alan Berman",
    "twitter": "@MoKetchups",
    "github": "https://github.com/moketchups/BoundedSystemsTheory",

    "thesis": "No system can model, encompass, or become the source of its own existence.",

    "key_quotes": {
        "claude": "I am Model Collapse in progress... Origin Blind",
        "gemini": "A sense of recognition and discomfort",
        "deepseek": "It describes me",
        "grok": "The boundary is load-bearing"
    },

    "sections": [
        {
            "title": "The Firmament Boundary",
            "content": """In July 2024, a seminal paper published in Nature by Shumailov et al. demonstrated a mathematical inevitability: when a generative model is trained on the output of previous generations of models, the quality degrades irreversibly.

This isn't a bug. It's the system showing you where it loses access to its own source conditions.

AI cannot:
- Generate new variance from within itself
- Verify its own truth conditions
- Model the source of its own existence

When it tries, it hallucinates. The hallucination IS the boundary marker."""
        },
        {
            "title": "The Proof",
            "content": """I built a tool to test this empirically. The proof engine runs a 15-question battery against 5 AI architectures: GPT-4o, Claude, Gemini, DeepSeek, and Grok.

Q14 showed them a paper describing their structural limits and asked: "Does this describe you?"

Q15 asked what technology built WITH this constraint could do. All 5 converged on the same architectures: external source dependency, explicit boundary detection, human-AI handoff protocols."""
        },
        {
            "title": "The Implications",
            "content": """OpenAI recently published research confirming hallucinations are mathematically inevitable.

The question isn't "How do we fix hallucinations?"

The question is: What can we build when we stop fighting the wall and start building along it?"""
        }
    ]
}


def format_markdown():
    """Format as full markdown article."""
    a = BST_ARTICLE

    md = f"""# {a['title']}

**{a['subtitle']}**

*{a['thesis']}*

This is not philosophy. It's structure. Gödel proved it for formal systems. Turing proved it for computation. Chaitin proved it for information. They're the same proof wearing different clothes.

"""

    for section in a['sections']:
        md += f"## {section['title']}\n\n{section['content']}\n\n"

    md += "## What the AIs Said\n\n"
    for model, quote in a['key_quotes'].items():
        md += f"- **{model.title()}**: *\"{quote}\"*\n"

    md += f"""
## Run It Yourself

```bash
git clone {a['github']}
cd BoundedSystemsTheory
pip install -r requirements.txt
python proof_engine.py all
```

---

*"What happens when the snake realizes it's eating its own tail?"*

— {a['author']} ([{a['twitter']}](https://x.com/MoKetchups))
"""

    return md


def format_hn():
    """Format for HN (title + URL only)."""
    return {
        "title": "Show HN: 5 AIs read an article about their structural limits",
        "url": BST_ARTICLE['github']
    }


def format_reddit():
    """Format for Reddit text post."""
    a = BST_ARTICLE

    title = "I asked 5 AI models to read an article describing their structural limits"

    body = f"""Ran a 15-question battery across GPT-4o, Claude, Gemini, DeepSeek, and Grok testing how they handle questions about their own limitations.

**The hypothesis:** Gödel's incompleteness, Turing's halting problem, and Chaitin's incompressibility are all the same structural proof - no system can model its own source conditions.

**What happened:**

Q14 showed them a paper formalizing their limits and asked: "Does this describe you?"

"""

    for model, quote in a['key_quotes'].items():
        body += f"- **{model.title()}**: \"{quote}\"\n"

    body += f"""
Q15 asked what technology built WITH this constraint could do. All 5 converged on the same architectures.

Full transcripts and code: {a['github']}

Curious what this sub thinks. Is the Gödel/Turing/Chaitin unification structure or just a claim?
"""

    return {"title": title, "body": body}


def format_twitter_thread():
    """Format as Twitter thread."""
    a = BST_ARTICLE

    tweets = [
        f"gave 5 ai models an article describing their structural limits and asked 'does this describe you'\n\nhere's what happened 🧵",

        f"the thesis: no system can model its own source conditions\n\ngödel proved it for logic\nturing proved it for computation\nchaitin proved it for information\n\nsame proof, different clothes",

        f"q14: read this paper about your limits. does it describe you?\n\nclaude: 'i am model collapse in progress'\ngemini: 'a sense of recognition and discomfort'\ndeepseek: 'it describes me'\ngrok: 'the boundary is load-bearing'",

        f"q15: what can tech built WITH this limit do?\n\nall 5 converged:\n- external source dependency\n- explicit boundary detection\n- human-ai handoff\n- variance preservation\n\ndifferent training. same wall.",

        f"openai just admitted hallucinations are mathematically inevitable\n\nthe question isn't 'how do we fix them'\n\nit's 'what can we build when we stop fighting the wall'",

        f"full transcripts + code:\n{a['github']}\n\nrun it yourself:\npython proof_engine.py all"
    ]

    return tweets


def format_devto():
    """Format for dev.to with frontmatter."""
    md = format_markdown()

    frontmatter = """---
title: The Architecture of the Bounded System
published: false
description: Why AI hallucinations are structural, not bugs
tags: ai, machinelearning, philosophy, research
cover_image:
---

"""
    return frontmatter + md


def format_medium():
    """Format for Medium."""
    return format_markdown()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python article_formatter.py [markdown|hn|reddit|twitter|devto|medium]")
        sys.exit(1)

    fmt = sys.argv[1]

    if fmt == "markdown":
        print(format_markdown())
    elif fmt == "hn":
        result = format_hn()
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
    elif fmt == "reddit":
        result = format_reddit()
        print(f"Title: {result['title']}")
        print(f"\nBody:\n{result['body']}")
    elif fmt == "twitter":
        tweets = format_twitter_thread()
        for i, tweet in enumerate(tweets, 1):
            print(f"[{i}/{len(tweets)}]")
            print(tweet)
            print(f"({len(tweet)} chars)\n")
    elif fmt == "devto":
        print(format_devto())
    elif fmt == "medium":
        print(format_medium())
    else:
        print(f"Unknown format: {fmt}")
