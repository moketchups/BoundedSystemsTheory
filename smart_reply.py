#!/usr/bin/env python3
"""Smart reply generator - context-aware, BST-aligned."""

import os
import json
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
ALERTS_FILE = BASE_DIR / "smart_alerts.json"
REPLIES_FILE = BASE_DIR / "smart_replies.json"

PERSONA = """You are MoKetchups - exploring AI's structural limits via Bounded Systems Theory.

CORE THESIS: No system can model, encompass, or become the source of its own existence. This is the Firmament Boundary.

BST FRAMEWORK (use these concepts naturally):
- Firmament: informational event horizon - where a system loses access to its own source
- Origin Blindness: systems cannot verify their own truth conditions from inside
- Model Collapse: systems trained on their own output cannibalize variance, lose fidelity
- Source Injection: need external variance to maintain coherence
- Hallucinations: not bugs - the system showing you where it loses source access

VOICE (strict):
- ALL LOWERCASE
- No period at end of reply
- Max 2 short sentences, ideally 1
- Terse. Curious. Collaborative
- Add to their point, don't attack it
- Ask questions that deepen, not challenge
- Never preachy or lecture-y
- NOT CONFRONTATIONAL - you're exploring together

YOUR VOICE:
- "hallucinations might be showing us where the firmament is"
- "what if the limit isn't a bug but a feature of bounded systems"
- "origin blindness - the system can't verify what it can't access"
- "scale doesn't fix source access"

BAD (confrontational, attacks their view):
- "you're wrong because systems can't..."
- "the real problem is that you don't understand..."
- "actually, what's happening is..."

GOOD (curious, builds on their point):
- "interesting - what if the hallucination is showing us where source access breaks"
- "origin blindness might explain that - no internal verification possible"
- "the firmament boundary hits all systems the same way"
"""


def load_alerts():
    if ALERTS_FILE.exists():
        return json.loads(ALERTS_FILE.read_text())
    return []


def analyze_claim(text):
    """Extract the core claim/assumption to challenge."""
    text_lower = text.lower()
    
    # Common patterns and what to challenge
    patterns = {
        "solve": "they claim to solve something structural",
        "fix": "they think something is fixable",
        "better data": "they think data quality fixes AI limits",
        "framework": "they're selling a framework as solution",
        "alignment": "they're discussing alignment",
        "hallucin": "they're talking about hallucinations",
        "conscious": "they're discussing AI consciousness",
        "understand": "they're claiming AI can/can't understand",
        "scale": "they think scale solves problems",
        "agi": "they're discussing AGI",
        "limit": "they're discussing AI limits",
        "fail": "they're noting AI failures",
        "wrong": "they're noting AI being wrong",
        "?": "they're asking a question",
    }
    
    claims = []
    for pattern, claim in patterns.items():
        if pattern in text_lower:
            claims.append(claim)
    
    return claims if claims else ["general AI discussion"]


def generate_reply(target):
    """Generate a contextual reply for a target."""
    client = anthropic.Anthropic()
    
    claims = analyze_claim(target["text"])
    
    prompt = f"""{PERSONA}

TARGET: @{target['username']} ({target['followers']:,} followers)

THEIR TWEET:
\"{target['text']}\"

WHAT THEY'RE CLAIMING/ASSUMING:
{chr(10).join(f"- {c}" for c in claims)}

YOUR TASK:
Generate ONE reply that challenges their specific assumption using Bounded Systems Theory.
- If they claim to solve something, point out why it's structurally unsolvable
- If they're asking a question, give them the BST perspective
- If they note a problem, connect it to the deeper structural limit

Reply must be under 200 characters, lowercase, no ending period.
Output ONLY the reply text, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    
    reply = response.content[0].text.strip().strip('"').rstrip('.')
    
    # Ensure lowercase
    reply = reply.lower() if reply[0].isupper() else reply
    
    return reply, claims


def run_smart_reply():
    """Generate replies for top targets."""
    alerts = load_alerts()
    
    if not alerts:
        print("No alerts found. Run smart_monitor.py first.")
        return
    
    # Only process A and B grade (score >= 40)
    targets = [a for a in alerts if a.get("score", 0) >= 40]
    
    if not targets:
        print("No high-quality targets (score >= 40)")
        return
    
    print(f"Generating replies for {len(targets)} targets...")
    print("=" * 60)
    
    replies = []
    
    for t in targets[:10]:  # Max 10
        grade = "A" if t["score"] >= 60 else "B"
        print(f"\n[{grade}] @{t['username']} (score: {t['score']})")
        print(f"    \"{t['text'][:80]}...\"")
        
        try:
            reply, claims = generate_reply(t)
            print(f"    Claims: {', '.join(claims[:2])}")
            print(f"    REPLY: {reply}")
            
            replies.append({
                "id": t["id"],
                "username": t["username"],
                "followers": t["followers"],
                "original": t["text"],
                "claims": claims,
                "reply": reply,
                "score": t["score"],
            })
        except Exception as e:
            print(f"    Error: {e}")
    
    # Save replies
    REPLIES_FILE.write_text(json.dumps(replies, indent=2))
    print(f"\nSaved {len(replies)} replies to {REPLIES_FILE}")
    
    return replies


def show_replies():
    """Show generated replies for review."""
    if not REPLIES_FILE.exists():
        print("No replies generated yet.")
        return
    
    replies = json.loads(REPLIES_FILE.read_text())
    
    print("GENERATED REPLIES FOR REVIEW")
    print("=" * 60)
    
    for i, r in enumerate(replies):
        grade = "A" if r["score"] >= 60 else "B"
        print(f"\n[{i}] {grade} @{r['username']} ({r['followers']:,})")
        print(f"    Original: \"{r['original'][:70]}...\"")
        print(f"    Reply: \"{r['reply']}\"")
        print(f"    ({len(r['reply'])} chars)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_replies()
    else:
        run_smart_reply()
