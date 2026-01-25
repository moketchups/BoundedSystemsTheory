#!/usr/bin/env python3
"""Find relevant accounts to follow."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("X_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def search_users(query):
    """Search for users by keyword in their recent tweets."""
    params = {
        "query": f"{query} -is:retweet lang:en",
        "max_results": 50,
        "tweet.fields": "author_id,public_metrics",
        "user.fields": "username,name,description,public_metrics,verified",
        "expansions": "author_id",
    }
    
    r = requests.get(
        "https://api.twitter.com/2/tweets/search/recent",
        headers=HEADERS,
        params=params,
    )
    
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        return []
    
    data = r.json()
    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
    return list(users.values())

def get_user(username):
    """Get single user info."""
    r = requests.get(
        f"https://api.twitter.com/2/users/by/username/{username}",
        headers=HEADERS,
        params={"user.fields": "description,public_metrics,verified"}
    )
    if r.status_code == 200:
        return r.json().get("data")
    return None

# Known relevant accounts in AI/consciousness/philosophy
SEED_ACCOUNTS = [
    "GaryMarcus",      # AI critic
    "fchollet",        # Keras, AI limits  
    "emilymbender",    # Linguistics, AI limits
    "melabordeaux",    # Complexity researcher
    "DrMichaelLevin",  # Biological cognition
    "erikhoel",        # Consciousness, info theory
    "AnilSeth",        # Consciousness researcher
    "JoshTenenbaum",   # Cognitive science
    "yaboradeaux",     # Philosophy of mind
    "ReligionProf",    # AI/hallucinations (from our scan)
]

print("RECOMMENDED FOLLOWS FOR @MoKetchups")
print("=" * 60)
print("\n[TIER 1] Known thought leaders in AI limits/consciousness:\n")

for username in SEED_ACCOUNTS:
    user = get_user(username)
    if user:
        followers = user.get("public_metrics", {}).get("followers_count", 0)
        desc = user.get("description", "")[:80]
        print(f"  @{user['username']} ({followers:,} followers)")
        print(f"    {desc}...")
        print()

# Search for more via relevant queries
print("\n[TIER 2] Active discussers (from recent tweets):\n")

queries = ["AI consciousness", "AI hallucination problem", "machine understanding"]
seen = set()

for q in queries:
    users = search_users(q)
    for u in users:
        username = u.get("username", "")
        if username.lower() in seen:
            continue
        seen.add(username.lower())
        
        followers = u.get("public_metrics", {}).get("followers_count", 0)
        following = u.get("public_metrics", {}).get("following_count", 0)
        
        # Filter: 1K-100K followers, follows others back
        if 1000 <= followers <= 100000 and following > 100:
            desc = u.get("description", "")[:60]
            ratio = followers / following if following else 0
            print(f"  @{username} ({followers:,} followers, ratio {ratio:.1f})")
            print(f"    {desc}...")
            print()
