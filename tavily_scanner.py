#!/usr/bin/env python3
"""
Tavily-powered scanner for finding high-value BST-relevant discussions.
Uses web search to find active conversations about AI limits, hallucinations, consciousness.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from tavily import TavilyClient
except ImportError:
    print("Install tavily: pip install tavily-python")
    exit(1)

BASE_DIR = Path(__file__).parent
TAVILY_ALERTS_FILE = BASE_DIR / "tavily_alerts.json"

# BST-relevant search queries
BST_QUERIES = [
    # Direct BST topics
    "AI hallucination mathematically inevitable",
    "AI consciousness impossible structural",
    "Gödel AI limits incompleteness",
    "AI cannot understand itself",
    "model collapse AI training",

    # Active discussions
    "AI hallucination problem site:x.com",
    "why does AI hallucinate site:x.com",
    "AI alignment unsolvable site:x.com",

    # Thought leaders
    "Gary Marcus AI limitations",
    "Francois Chollet AI consciousness",
    "AI safety Gödel",
]


def scan_web():
    """Scan web for BST-relevant discussions."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    all_results = []
    seen_urls = set()

    print("TAVILY SCANNER - Finding BST-Relevant Discussions")
    print("=" * 60)

    for query in BST_QUERIES:
        print(f"\nSearching: {query[:50]}...")

        try:
            results = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
            )

            for r in results.get("results", []):
                url = r.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                # Score relevance
                content = r.get("content", "").lower()
                title = r.get("title", "").lower()

                score = 0
                bst_terms = ["hallucin", "limit", "conscious", "gödel", "goedel",
                            "bounded", "structural", "inevitable", "impossible",
                            "cannot", "self-reference", "incompleteness"]

                for term in bst_terms:
                    if term in content or term in title:
                        score += 10

                # Boost X/Twitter links
                if "x.com" in url or "twitter.com" in url:
                    score += 20

                # Boost recent news
                if "2026" in content or "2025" in content:
                    score += 10

                all_results.append({
                    "title": r.get("title", ""),
                    "url": url,
                    "content": r.get("content", "")[:500],
                    "score": score,
                    "query": query,
                    "found_at": datetime.now().isoformat(),
                })

        except Exception as e:
            print(f"  Error: {e}")

    # Sort by score
    all_results.sort(key=lambda x: x["score"], reverse=True)

    # Show top results
    print("\n" + "=" * 60)
    print("TOP BST-RELEVANT FINDINGS:")
    print("=" * 60)

    for r in all_results[:15]:
        print(f"\n[Score: {r['score']}] {r['title'][:60]}")
        print(f"  URL: {r['url']}")
        print(f"  {r['content'][:150]}...")

    # Save results
    TAVILY_ALERTS_FILE.write_text(json.dumps(all_results, indent=2))
    print(f"\nSaved {len(all_results)} results to {TAVILY_ALERTS_FILE}")

    return all_results


def find_twitter_targets():
    """Extract X/Twitter links from Tavily results for engagement."""
    if not TAVILY_ALERTS_FILE.exists():
        print("No Tavily results. Run scan first.")
        return []

    results = json.loads(TAVILY_ALERTS_FILE.read_text())

    twitter_targets = []
    for r in results:
        url = r.get("url", "")
        if "x.com" in url or "twitter.com" in url:
            # Extract tweet ID if possible
            parts = url.split("/")
            if "status" in parts:
                idx = parts.index("status")
                if idx + 1 < len(parts):
                    tweet_id = parts[idx + 1].split("?")[0]
                    twitter_targets.append({
                        "url": url,
                        "tweet_id": tweet_id,
                        "title": r.get("title", ""),
                        "score": r.get("score", 0),
                    })

    return twitter_targets


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "twitter":
        targets = find_twitter_targets()
        print(f"\nFound {len(targets)} Twitter targets:")
        for t in targets:
            print(f"  {t['tweet_id']}: {t['title'][:50]}...")
    else:
        scan_web()
