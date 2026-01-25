#!/usr/bin/env python3
"""Smart monitor - humans only, reply-likelihood scoring, bot detection."""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
ALERTS_FILE = BASE_DIR / "smart_alerts.json"
SEEN_FILE = BASE_DIR / "smart_seen.json"

TOKEN = os.getenv("X_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Known bot/AI accounts
BOT_ACCOUNTS = {
    "grok", "openai", "anthropicai", "googleai", "claudeai", "gemini",
    "chatgpt", "perplexity_ai", "deepseek_ai", "mistralai",
}

# AI-assisted account patterns (jargon, perfect grammar, framework-pushers)
AI_JARGON = [
    "endogenous", "equilibrium-seeking", "tyag force", "ule predicts",
    "framework", "ecosystem", "tokenomics", "web3", "sovereign data",
    "ground truth provider", "coordination layer",
]

# Human signals
HUMAN_SIGNALS = [
    "?",  # questions
    "...",  # trailing off
    "lol", "lmao", "wtf", "tbh", "imo", "idk",
    "i think", "i feel", "i don't", "i cant", "i can't",
    "frustrat", "confus", "annoy", "weird", "strange",
]


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(list(seen)[-2000:]))


def is_bot_account(username):
    """Check if account is a known bot."""
    return username.lower() in BOT_ACCOUNTS


def detect_ai_generated(text):
    """Score likelihood of AI-generated content. Higher = more likely AI."""
    text_lower = text.lower()
    score = 0
    
    # AI jargon
    for jargon in AI_JARGON:
        if jargon in text_lower:
            score += 20
    
    # Perfect structure (no typos, complete sentences)
    if text_lower == text.lower() and text[0].isupper():
        # Starts with capital, proper structure
        score += 5
    
    # No human signals
    has_human = any(sig in text_lower for sig in HUMAN_SIGNALS)
    if not has_human:
        score += 15
    
    # Overly long and structured
    if len(text) > 250 and "\n" in text:
        score += 10
    
    return min(score, 100)


def get_user_reply_rate(username):
    """Check if user actually replies to others (human behavior)."""
    try:
        params = {
            "query": f"from:{username}",
            "max_results": 20,
            "tweet.fields": "in_reply_to_user_id",
        }
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=HEADERS,
            params=params,
        )
        if r.status_code == 200:
            tweets = r.json().get("data", [])
            if not tweets:
                return 0.0
            replies = sum(1 for t in tweets if t.get("in_reply_to_user_id"))
            return replies / len(tweets)
    except:
        pass
    return 0.5  # default


def score_target(tweet, user_info):
    """Score a potential engagement target. Higher = better."""
    score = 0
    reasons = []
    
    username = user_info.get("username", "")
    followers = user_info.get("public_metrics", {}).get("followers_count", 0)
    following = user_info.get("public_metrics", {}).get("following_count", 0)
    text = tweet.get("text", "")
    metrics = tweet.get("public_metrics", {})
    
    # === DISQUALIFIERS ===
    
    # Bot account
    if is_bot_account(username):
        return -1, ["DISQUALIFIED: Bot account"]
    
    # AI-generated content
    ai_score = detect_ai_generated(text)
    if ai_score >= 50:
        return -1, [f"DISQUALIFIED: AI-generated ({ai_score}%)"]
    
    # === POSITIVE SIGNALS ===
    
    # Follower sweet spot (1K-50K)
    if 1000 <= followers <= 50000:
        score += 20
        reasons.append(f"followers in range: +20")
    elif 500 <= followers <= 100000:
        score += 10
        reasons.append(f"followers ok: +10")
    else:
        reasons.append(f"followers out of range: +0")
    
    # They follow people back (human behavior)
    if following > 0:
        ratio = followers / following
        if 0.5 <= ratio <= 3:
            score += 15
            reasons.append(f"healthy f/f ratio ({ratio:.1f}): +15")
    else:
        score -= 10
        reasons.append(f"follows nobody: -10")
    
    # Existing engagement (active thread)
    likes = metrics.get("like_count", 0)
    replies = metrics.get("reply_count", 0)
    rts = metrics.get("retweet_count", 0)
    engagement = likes + replies * 2 + rts * 3
    
    if engagement > 50:
        score += 20
        reasons.append(f"high engagement ({engagement}): +20")
    elif engagement > 10:
        score += 10
        reasons.append(f"medium engagement ({engagement}): +10")
    
    # Human signals in text
    text_lower = text.lower()
    human_count = sum(1 for sig in HUMAN_SIGNALS if sig in text_lower)
    if human_count >= 2:
        score += 15
        reasons.append(f"human signals ({human_count}): +15")
    elif human_count == 1:
        score += 8
        reasons.append(f"some human signal: +8")
    
    # Questions (they want engagement)
    if "?" in text:
        score += 10
        reasons.append("asking question: +10")
    
    # BST relevance
    bst_terms = ["conscious", "hallucin", "align", "limit", "understand", 
                 "sentient", "agi", "reason", "comprehend", "fail", "wrong"]
    bst_matches = sum(1 for t in bst_terms if t in text_lower)
    if bst_matches >= 2:
        score += 15
        reasons.append(f"BST relevant ({bst_matches} terms): +15")
    elif bst_matches == 1:
        score += 8
        reasons.append(f"somewhat relevant: +8")
    
    # Low AI score (definitely human)
    if ai_score < 20:
        score += 10
        reasons.append(f"definitely human (AI:{ai_score}%): +10")
    
    return score, reasons


def search_targets(queries, max_age_minutes=120):
    """Search for engagement targets."""
    start_time = (datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    all_tweets = []
    seen_ids = set()
    
    for query in queries:
        params = {
            "query": f"{query} -is:retweet -is:reply lang:en",
            "max_results": 25,
            "start_time": start_time,
            "tweet.fields": "author_id,created_at,public_metrics",
            "user.fields": "username,public_metrics",
            "expansions": "author_id",
        }
        
        try:
            r = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=HEADERS,
                params=params,
            )
            if r.status_code == 200:
                data = r.json()
                tweets = data.get("data", [])
                users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                
                for t in tweets:
                    if t["id"] not in seen_ids:
                        seen_ids.add(t["id"])
                        user = users.get(t["author_id"], {})
                        all_tweets.append((t, user, query))
        except Exception as e:
            print(f"  Error on '{query}': {e}")
    
    return all_tweets


def run_smart_scan():
    """Run one smart scan cycle."""
    print("=" * 60)
    print("SMART MONITOR - Humans Only")
    print("=" * 60)
    print()
    
    seen = load_seen()
    
    queries = [
        "AI hallucination",
        "LLM wrong",
        "ChatGPT mistake",
        "AI doesn't understand",
        "why does AI",
        "AI limitation",
        "can AI be conscious",
        "AI alignment problem",
    ]
    
    print(f"Searching {len(queries)} queries (last 2 hours)...")
    results = search_targets(queries)
    print(f"Found {len(results)} tweets")
    print()
    
    # Score all targets
    scored = []
    disqualified = 0
    
    for tweet, user, query in results:
        if tweet["id"] in seen:
            continue
        
        score, reasons = score_target(tweet, user)
        
        if score < 0:
            disqualified += 1
            continue
        
        scored.append({
            "id": tweet["id"],
            "username": user.get("username", "?"),
            "followers": user.get("public_metrics", {}).get("followers_count", 0),
            "following": user.get("public_metrics", {}).get("following_count", 0),
            "text": tweet["text"],
            "score": score,
            "reasons": reasons,
            "likes": tweet.get("public_metrics", {}).get("like_count", 0),
            "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
            "query": query,
        })
        
        seen.add(tweet["id"])
    
    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"Disqualified (bots/AI): {disqualified}")
    print(f"Qualified humans: {len(scored)}")
    print()
    
    # Show top targets
    if scored:
        print("TOP TARGETS (Grade A = 60+, B = 40+, C = 20+):")
        print("-" * 60)
        
        for t in scored[:10]:
            grade = "A" if t["score"] >= 60 else "B" if t["score"] >= 40 else "C" if t["score"] >= 20 else "D"
            print(f"\n[{grade}] @{t['username']} ({t['followers']:,} followers) - Score: {t['score']}")
            print(f"    Following: {t['following']:,} | Likes: {t['likes']} | Replies: {t['replies']}")
            print(f"    \"{t['text'][:100]}...\"")
            print(f"    Scoring: {', '.join(t['reasons'][:3])}")
        
        # Save top targets
        ALERTS_FILE.write_text(json.dumps(scored[:20], indent=2))
        print(f"\nSaved top {min(20, len(scored))} targets to {ALERTS_FILE}")
    
    save_seen(seen)
    return scored


if __name__ == "__main__":
    run_smart_scan()
