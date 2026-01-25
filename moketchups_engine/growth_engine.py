#!/usr/bin/env python3
"""Growth engine for generating MoKetchups replies."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Install anthropic: pip install anthropic")
    sys.exit(1)

from config import PERSONA

BASE_DIR = Path(__file__).parent
ALERTS_FILE = BASE_DIR / "alerts.json"
QUEUE_FILE = BASE_DIR / "reply_queue.json"


def load_alerts() -> list:
    """Load pending alerts."""
    if ALERTS_FILE.exists():
        return json.loads(ALERTS_FILE.read_text())
    return []


def load_queue() -> list:
    """Load reply queue."""
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def save_queue(queue: list):
    """Save reply queue."""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def generate_reply(client: anthropic.Anthropic, tweet: dict) -> str:
    """Generate a reply using Claude."""
    prompt = f"""{PERSONA}

Tweet to reply to:
@{tweet['username']} ({tweet['followers']} followers):
"{tweet['text']}"

Generate a single reply. Be terse, provocative, insightful. No periods at end. Under 280 chars.
Reply only with the text of the reply, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )

    reply = response.content[0].text.strip()

    # Clean up
    reply = reply.strip('"\'')
    if reply.endswith('.'):
        reply = reply[:-1]

    return reply


def cmd_scan():
    """Scan alerts and generate replies."""
    alerts = load_alerts()
    if not alerts:
        print("No alerts to process.")
        return

    queue = load_queue()
    existing_ids = {item.get("reply_to_id") for item in queue}

    client = anthropic.Anthropic()

    new_count = 0
    for alert in alerts:
        if alert["id"] in existing_ids:
            continue

        print(f"\nGenerating reply for @{alert['username']}...")
        print(f'  "{alert["text"][:80]}..."')

        try:
            reply = generate_reply(client, alert)
            print(f'  Reply: "{reply}"')

            queue_item = {
                "id": len(queue),
                "reply_to_id": alert["id"],
                "reply_to_username": alert["username"],
                "reply_to_text": alert["text"],
                "reply_to_followers": alert["followers"],
                "reply_to_likes": alert.get("likes", 0),
                "reply": reply,
                "generated_at": datetime.now().isoformat(),
                "status": "pending",
            }
            queue.append(queue_item)
            new_count += 1

        except Exception as e:
            print(f"  Error: {e}")

    save_queue(queue)
    print(f"\nGenerated {new_count} new replies. Total in queue: {len(queue)}")
    print("Use 'growth_engine.py queue' to review, 'growth_engine.py approve <ids>' to approve.")


def cmd_queue():
    """Show reply queue."""
    queue = load_queue()
    pending = [q for q in queue if q["status"] == "pending"]

    if not pending:
        print("No pending replies.")
        return

    print(f"\n{len(pending)} pending replies:\n")
    for item in pending:
        print(f"[{item['id']}] @{item['reply_to_username']} ({item['reply_to_followers']} followers)")
        print(f'    Tweet: "{item["reply_to_text"][:60]}..."')
        print(f'    Reply: "{item["reply"]}"')
        print()


def cmd_approve(ids: list):
    """Approve specific replies."""
    queue = load_queue()
    approved = 0

    for item in queue:
        if item["id"] in ids and item["status"] == "pending":
            item["status"] = "approved"
            approved += 1
            print(f"Approved [{item['id']}]: {item['reply'][:50]}...")

    save_queue(queue)
    print(f"\nApproved {approved} replies. Use cookie_poster.py to post them.")


def cmd_reject(ids: list):
    """Reject specific replies."""
    queue = load_queue()
    rejected = 0

    for item in queue:
        if item["id"] in ids:
            item["status"] = "rejected"
            rejected += 1
            print(f"Rejected [{item['id']}]")

    save_queue(queue)
    print(f"\nRejected {rejected} replies.")


def cmd_edit(item_id: int, new_text: str):
    """Edit a reply."""
    queue = load_queue()

    for item in queue:
        if item["id"] == item_id:
            old = item["reply"]
            item["reply"] = new_text
            save_queue(queue)
            print(f"Updated [{item_id}]:")
            print(f"  Old: {old}")
            print(f"  New: {new_text}")
            return

    print(f"Reply {item_id} not found.")


def cmd_clear():
    """Clear alerts file."""
    if ALERTS_FILE.exists():
        ALERTS_FILE.unlink()
    print("Cleared alerts.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python growth_engine.py [scan|queue|approve|reject|edit|clear]")
        print("  scan          - Generate replies for new alerts")
        print("  queue         - Show pending replies")
        print("  approve 0 1 2 - Approve replies by ID")
        print("  reject 0 1    - Reject replies by ID")
        print("  edit 0 'text' - Edit a reply")
        print("  clear         - Clear alerts")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        cmd_scan()
    elif cmd == "queue":
        cmd_queue()
    elif cmd == "approve":
        ids = [int(x) for x in sys.argv[2:]]
        cmd_approve(ids)
    elif cmd == "reject":
        ids = [int(x) for x in sys.argv[2:]]
        cmd_reject(ids)
    elif cmd == "edit":
        item_id = int(sys.argv[2])
        new_text = sys.argv[3]
        cmd_edit(item_id, new_text)
    elif cmd == "clear":
        cmd_clear()
    else:
        print(f"Unknown command: {cmd}")
