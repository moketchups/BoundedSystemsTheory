#!/usr/bin/env python3
"""
Track repo metrics over time.
Run weekly to document growth.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

METRICS_FILE = Path(__file__).parent / "metrics_history.json"

def get_metrics():
    """Fetch current metrics from GitHub API."""
    # Views
    views = subprocess.run(
        ["gh", "api", "repos/moketchups/BoundedSystemsTheory/traffic/views"],
        capture_output=True, text=True
    )
    views_data = json.loads(views.stdout) if views.returncode == 0 else {}

    # Clones
    clones = subprocess.run(
        ["gh", "api", "repos/moketchups/BoundedSystemsTheory/traffic/clones"],
        capture_output=True, text=True
    )
    clones_data = json.loads(clones.stdout) if clones.returncode == 0 else {}

    # Stars and forks
    repo = subprocess.run(
        ["gh", "repo", "view", "moketchups/BoundedSystemsTheory", "--json", "stargazerCount,forkCount"],
        capture_output=True, text=True
    )
    repo_data = json.loads(repo.stdout) if repo.returncode == 0 else {}

    return {
        "timestamp": datetime.now().isoformat(),
        "views_total": views_data.get("count", 0),
        "views_unique": views_data.get("uniques", 0),
        "clones_total": clones_data.get("count", 0),
        "clones_unique": clones_data.get("uniques", 0),
        "stars": repo_data.get("stargazerCount", 0),
        "forks": repo_data.get("forkCount", 0),
    }

def load_history():
    """Load existing metrics history."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    """Save metrics history."""
    with open(METRICS_FILE, "w") as f:
        json.dump(history, f, indent=2)

def main():
    print("Fetching current metrics...")
    metrics = get_metrics()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  BST Repo Metrics — {metrics['timestamp'][:10]}
╠══════════════════════════════════════════════════════════════════════╣
║  Views:  {metrics['views_total']:>6} total  |  {metrics['views_unique']:>6} unique
║  Clones: {metrics['clones_total']:>6} total  |  {metrics['clones_unique']:>6} unique
║  Stars:  {metrics['stars']:>6}        |  Forks: {metrics['forks']:>6}
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Load history and append
    history = load_history()
    history.append(metrics)
    save_history(history)

    print(f"Saved to {METRICS_FILE}")

    # Show trend if we have history
    if len(history) > 1:
        prev = history[-2]
        print(f"\nSince last check ({prev['timestamp'][:10]}):")
        print(f"  Clones: {prev['clones_unique']} → {metrics['clones_unique']} ({metrics['clones_unique'] - prev['clones_unique']:+d})")
        print(f"  Stars:  {prev['stars']} → {metrics['stars']} ({metrics['stars'] - prev['stars']:+d})")

    # Shadow interest ratio
    if metrics['clones_unique'] > 0:
        ratio = metrics['stars'] / metrics['clones_unique']
        print(f"\nShadow Interest Ratio: {ratio:.1%} (stars/unique cloners)")
        print(f"  {metrics['clones_unique']} people downloaded. {metrics['stars']} publicly endorsed.")

if __name__ == "__main__":
    main()
