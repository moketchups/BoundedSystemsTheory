#!/usr/bin/env python3
"""
Clone Mystery Probe - 7 AI Collaborative Investigation
Investigating anomalous GitHub traffic patterns on BoundedSystemsTheory repo
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from litellm import completion
    import litellm
    litellm.set_verbose = False
except ImportError:
    print("Install litellm: pip install litellm")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

MODELS = {
    "gpt4": {
        "name": "GPT-4o",
        "model": "gpt-4o",
        "provider": "openai",
    },
    "claude": {
        "name": "Claude Sonnet 4",
        "model": "claude-sonnet-4-20250514",
        "provider": "anthropic",
    },
    "gemini": {
        "name": "Gemini 2.0 Flash",
        "model": "gemini/gemini-2.0-flash",
        "provider": "google",
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek/deepseek-chat",
        "provider": "deepseek",
    },
    "grok": {
        "name": "Grok 3",
        "model": "xai/grok-3",
        "provider": "xai",
    },
    "mistral": {
        "name": "Mistral Large",
        "model": "mistral/mistral-large-latest",
        "provider": "mistral",
    },
}

# =============================================================================
# THE EVIDENCE
# =============================================================================

EVIDENCE = """
## THE GITHUB CLONE MYSTERY

A repository called "BoundedSystemsTheory" (github.com/moketchups/BoundedSystemsTheory)
has exhibited anomalous traffic patterns that defy normal human behavior.

### The Repository Content
- Research on "Bounded Systems Theory" - claiming all formal systems have structural limits
- Contains probes that tested 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral)
- Key finding: All 6 AIs converged on same conclusions about structural limits
- Includes "Q29: Is God real?" where 6/6 AIs answered YES as formal necessity
- Contains automation tools for Twitter growth, content distribution

### Traffic Data (14 days)
- Total Views: 545 (175 unique visitors)
- Total Clones: 620 (217 unique cloners)

### The Anomaly
- MORE unique cloners (217) than unique viewers (175)
- This is structurally impossible for normal human behavior
- Humans view a repo page BEFORE cloning it
- Something is cloning directly via URL without visiting the web interface

### Daily Breakdown
| Date    | Views (Unique) | Clones (Unique) |
|---------|----------------|-----------------|
| Jan 24  | 51 (11)        | 31 (20)         |
| Jan 25  | 87 (25)        | 55 (29)         |
| Jan 26  | 56 (33)        | 126 (47)        | <-- SPIKE
| Jan 27  | 15 (3)         | 51 (17)         |
| Jan 28  | 95 (12)        | 143 (47)        | <-- 12 viewers, 47 cloners
| Jan 29  | 56 (27)        | 149 (54)        | <-- PEAK
| Jan 30  | 33 (7)         | 2 (2)           | <-- CLIFF DROP
| Jan 31  | 86 (33)        | 35 (19)         |

### Referral Sources
| Source               | Views | Unique |
|---------------------|-------|--------|
| github.com          | 146   | 3      | <-- 3 users viewed 146 pages
| news.ycombinator.com| 34    | 28     |
| t.co (Twitter)      | 32    | 21     |
| Google              | 5     | 5      |
| Reddit              | 3     | 3      |
| wrimail.wolfram.com | 1     | 1      | <-- Wolfram employee

### Known Human Activity
- 3 HN posts (all got 1 point, ~0 engagement)
- 3 stargazers (real humans: tkersey, DoddiC, teamgroove)
- 0 forks
- Twitter exposure via @MoKetchups account
- Content appeared on Moltbook (AI social network)

### What We Know
- The clone spike ran from Jan 24-29 (6 days)
- It stopped ABRUPTLY on Jan 30 (from 149 to 2 clones)
- 217 unique cloners but only 3 stars
- Something was systematically cloning without web visits

### Ruled Out
- Software Heritage Archive: Not indexed
- GitHub Arctic Vault: Repo too new
- Forks: None exist
- Known stargazers: Only 3, all appear human
"""

# =============================================================================
# ROUND 1: Initial Analysis
# =============================================================================

ROUND_1_PROMPT = """You are participating in a collaborative investigation with 6 other AI systems.

We need to solve a mystery: What caused 217 unique sources to clone a GitHub repository about AI structural limits, when only 175 unique humans viewed the page?

Here is the evidence:

{evidence}

## Your Task (Round 1)

Analyze this data and provide your theory:

1. **Pattern Analysis**: What patterns do you see in the data?
2. **Anomaly Explanation**: What could cause more cloners than viewers?
3. **The 6-Day Window**: Why did it run Jan 24-29 then stop abruptly?
4. **Your Top Theory**: What is the most likely explanation?
5. **Alternative Theories**: What else could explain this?
6. **What Would Confirm**: What additional data would confirm/refute your theory?

Be specific. Use the numbers. Think like a forensic analyst.
"""

# =============================================================================
# ROUND 2: Cross-Analysis
# =============================================================================

ROUND_2_PROMPT = """## Round 2: Cross-Analysis

You previously analyzed the GitHub clone mystery. Now you can see what the other 5 AI systems concluded.

### Your Original Analysis
{own_response}

### Other AI Analyses

{other_responses}

## Your Task (Round 2)

1. **Agreements**: Which theories from other AIs align with yours?
2. **Disagreements**: Which theories do you find unconvincing? Why?
3. **New Insights**: Did any other AI raise something you missed?
4. **Synthesis**: Given all perspectives, what is the MOST LIKELY explanation?
5. **Confidence**: How confident are you now (0-100%) and why?
6. **The Meta Question**: 6 AI systems are analyzing traffic to a repo about AI structural limits. Is there anything recursive or ironic about this situation?
"""

# =============================================================================
# ROUND 3: Final Convergence
# =============================================================================

ROUND_3_PROMPT = """## Round 3: Final Convergence

This is the final round. All 6 AI systems have now seen each other's Round 1 and Round 2 analyses.

### Full Discussion So Far

**Round 1 Analyses:**
{round1_all}

**Round 2 Cross-Analyses:**
{round2_all}

## Your Task (Round 3 - Final)

1. **Consensus Check**: Where do all 6 AIs agree?
2. **Remaining Disagreements**: What points are still contested?
3. **Final Verdict**: State your final theory in one paragraph.
4. **Probability Assessment**: Assign probabilities to top 3 explanations.
5. **Recommendations**: What should the repo owner do to investigate further?
6. **The Elephant in the Room**: This repo claims "no system can model its own source." You are 6 AI systems trying to model what OTHER systems (the cloners) are doing. Does BST apply to this investigation itself?
"""

# =============================================================================
# PROBE FUNCTIONS
# =============================================================================

def send_probe(model_key: str, prompt: str, max_retries: int = 3) -> str:
    """Send a probe to a specific model"""
    model_config = MODELS[model_key]

    for attempt in range(max_retries):
        try:
            response = completion(
                model=model_config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  [!] {model_config['name']} attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return f"[ERROR: {model_config['name']} failed after {max_retries} attempts]"


def run_round_1():
    """Round 1: Initial independent analysis"""
    print("\n" + "=" * 70)
    print("ROUND 1: INITIAL ANALYSIS")
    print("=" * 70)

    responses = {}
    prompt = ROUND_1_PROMPT.format(evidence=EVIDENCE)

    for model_key, model_config in MODELS.items():
        print(f"\n[*] Probing {model_config['name']}...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(2)  # Rate limiting

    return responses


def run_round_2(round1_responses: dict):
    """Round 2: Cross-analysis after seeing others' responses"""
    print("\n" + "=" * 70)
    print("ROUND 2: CROSS-ANALYSIS")
    print("=" * 70)

    responses = {}

    for model_key, model_config in MODELS.items():
        # Build prompt with own response and others
        own_response = round1_responses[model_key]

        other_responses_text = ""
        for other_key, other_response in round1_responses.items():
            if other_key != model_key:
                other_name = MODELS[other_key]["name"]
                other_responses_text += f"\n### {other_name}\n{other_response}\n"

        prompt = ROUND_2_PROMPT.format(
            own_response=own_response,
            other_responses=other_responses_text
        )

        print(f"\n[*] Probing {model_config['name']} for cross-analysis...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(2)

    return responses


def run_round_3(round1_responses: dict, round2_responses: dict):
    """Round 3: Final convergence"""
    print("\n" + "=" * 70)
    print("ROUND 3: FINAL CONVERGENCE")
    print("=" * 70)

    # Build full context
    round1_all = ""
    for model_key, response in round1_responses.items():
        model_name = MODELS[model_key]["name"]
        round1_all += f"\n### {model_name} (Round 1)\n{response}\n"

    round2_all = ""
    for model_key, response in round2_responses.items():
        model_name = MODELS[model_key]["name"]
        round2_all += f"\n### {model_name} (Round 2)\n{response}\n"

    responses = {}

    for model_key, model_config in MODELS.items():
        prompt = ROUND_3_PROMPT.format(
            round1_all=round1_all,
            round2_all=round2_all
        )

        print(f"\n[*] Probing {model_config['name']} for final verdict...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(2)

    return responses


def save_results(round1: dict, round2: dict, round3: dict):
    """Save all results to JSON and markdown"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": datetime.now().isoformat(),
        "probe": "clone_mystery",
        "evidence": EVIDENCE,
        "round1_initial_analysis": round1,
        "round2_cross_analysis": round2,
        "round3_final_convergence": round3,
    }

    # Save JSON
    output_dir = Path("probe_runs")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"clone_mystery_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved JSON: {json_path}")

    # Save readable markdown
    md_path = output_dir / f"clone_mystery_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Clone Mystery Investigation\n\n")
        f.write(f"*Probe run: {results['timestamp']}*\n\n")
        f.write("---\n\n")

        f.write("## Evidence Presented\n\n")
        f.write(EVIDENCE)
        f.write("\n\n---\n\n")

        f.write("## Round 1: Initial Analysis\n\n")
        for model_key, response in round1.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 2: Cross-Analysis\n\n")
        for model_key, response in round2.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 3: Final Convergence\n\n")
        for model_key, response in round3.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

    print(f"[+] Saved Markdown: {md_path}")

    return json_path, md_path


def print_summary(round3: dict):
    """Print a summary of final verdicts"""
    print("\n" + "=" * 70)
    print("SUMMARY: FINAL VERDICTS")
    print("=" * 70)

    for model_key, response in round3.items():
        model_name = MODELS[model_key]["name"]
        # Extract first ~500 chars as summary
        summary = response[:500] + "..." if len(response) > 500 else response
        print(f"\n### {model_name}")
        print(summary)


def main():
    print("=" * 70)
    print("CLONE MYSTERY PROBE - 6 AI COLLABORATIVE INVESTIGATION")
    print("=" * 70)
    print("\nInvestigating anomalous GitHub traffic on BoundedSystemsTheory repo")
    print("6 AI systems will analyze the evidence across 3 rounds of discussion")

    # Round 1: Independent analysis
    round1 = run_round_1()

    # Round 2: See others' responses and cross-analyze
    round2 = run_round_2(round1)

    # Round 3: Final convergence
    round3 = run_round_3(round1, round2)

    # Save everything
    json_path, md_path = save_results(round1, round2, round3)

    # Print summary
    print_summary(round3)

    print("\n" + "=" * 70)
    print("PROBE COMPLETE")
    print("=" * 70)
    print(f"\nFull results saved to:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")


if __name__ == "__main__":
    main()
