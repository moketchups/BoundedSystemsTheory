#!/usr/bin/env python3
"""Follow accounts via X API."""

import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()

# OAuth 1.0a for write actions
auth = OAuth1(
    os.getenv("X_CONSUMER_KEY"),
    os.getenv("X_CONSUMER_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_TOKEN_SECRET"),
)

BEARER = os.getenv("X_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {BEARER}"}

def get_my_user_id():
    """Get authenticated user's ID."""
    r = requests.get(
        "https://api.twitter.com/2/users/me",
        auth=auth,
    )
    if r.status_code == 200:
        return r.json()["data"]["id"]
    print(f"Error getting user: {r.status_code} - {r.text}")
    return None

def get_user_id(username):
    """Get user ID from username."""
    r = requests.get(
        f"https://api.twitter.com/2/users/by/username/{username}",
        headers=HEADERS,
    )
    if r.status_code == 200:
        return r.json().get("data", {}).get("id")
    return None

def follow_user(my_id, target_id, target_username):
    """Follow a user."""
    r = requests.post(
        f"https://api.twitter.com/2/users/{my_id}/following",
        auth=auth,
        json={"target_user_id": target_id},
    )
    if r.status_code == 200:
        result = r.json().get("data", {})
        if result.get("following"):
            return "followed"
        elif result.get("pending_follow"):
            return "pending"
    elif r.status_code == 403:
        return "no_permission"
    elif r.status_code == 429:
        return "rate_limited"
    return f"error:{r.status_code}"

# Accounts to follow
TARGETS = [
    "GaryMarcus",
    "fchollet",
    "emilymbender",
    "drmichaellevin",
    "AnilKSeth",
    "erik_p_hoel",
    "Plinz",  # Joscha Bach
    "ReligionProf",
    "SteveKlinko",
]

print("Following accounts for @MoKetchups...")
print("=" * 50)

my_id = get_my_user_id()
if not my_id:
    print("Could not authenticate. Check API credentials.")
    exit(1)

print(f"Authenticated as user ID: {my_id}\n")

for username in TARGETS:
    target_id = get_user_id(username)
    if not target_id:
        print(f"  @{username}: not found")
        continue
    
    result = follow_user(my_id, target_id, username)
    print(f"  @{username}: {result}")

print("\nDone.")
