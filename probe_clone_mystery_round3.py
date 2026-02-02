#!/usr/bin/env python3
"""
Clone Mystery Probe Round 3 - Reverse Engineering Value & Motives
Deep analysis of gaps, incentives, and what the data reveals vs conceals
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

MODELS = {
    "gpt4": {"name": "GPT-4o", "model": "gpt-4o", "provider": "openai"},
    "claude": {"name": "Claude Sonnet 4", "model": "claude-sonnet-4-20250514", "provider": "anthropic"},
    "gemini": {"name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash", "provider": "google"},
    "deepseek": {"name": "DeepSeek V3", "model": "deepseek/deepseek-chat", "provider": "deepseek"},
    "grok": {"name": "Grok 3", "model": "xai/grok-3", "provider": "xai"},
    "mistral": {"name": "Mistral Large", "model": "mistral/mistral-large-latest", "provider": "mistral"},
}

# =============================================================================
# FULL CONTEXT - ALL DATA WE HAVE
# =============================================================================

FULL_CONTEXT = """
## CLONE MYSTERY - ROUND 3: REVERSE ENGINEERING VALUE & MOTIVES

We've done two rounds of analysis. Now let's go deeper.

---

## THE COMPLETE DATA SET

### Traffic Numbers
- Views: 545 total (175 unique)
- Clones: 620 total (217 unique)
- Stars: 3
- Forks: 0
- Watchers: 1

### Temporal Pattern
| Date | Views (Unique) | Clones (Unique) |
|------|----------------|-----------------|
| Jan 19 | 1 (1) | 0 (0) | ← Repo created
| Jan 20-23 | 0-1 | 0 | ← Dormant
| Jan 24 | 51 (11) | 31 (20) | ← First spike
| Jan 25 | 87 (25) | 55 (29) | ← Growing
| Jan 26 | 56 (33) | 126 (47) | ← Clone explosion
| Jan 27 | 15 (3) | 51 (17) | ← Views drop, clones continue
| Jan 28 | 95 (12) | 143 (47) | ← 12 viewers, 47 cloners
| Jan 29 | 56 (27) | 149 (54) | ← Peak clones
| Jan 30 | 33 (7) | 2 (2) | ← CLIFF DROP
| Jan 31 | 86 (33) | 35 (19) | ← Partial recovery
| Feb 1 | 64 (43) | 28 (14) | ← Normalizing

### Referral Sources
| Source | Views | Unique | Notes |
|--------|-------|--------|-------|
| github.com | 146 | 3 | Internal navigation - 3 users, 146 pages |
| news.ycombinator.com | 34 | 28 | HN traffic |
| t.co (Twitter) | 32 | 21 | Twitter referrals |
| Google | 5 | 5 | Organic search |
| Reddit | 3 | 3 | Reddit referrals |
| wrimail.wolfram.com | 1 | 1 | Wolfram employee |

### Known Human Actors
- **3 Stargazers**: tkersey (GitHub user #217, OG), DoddiC, teamgroove
- **HN Posts**: 3 submissions, all got 1 point (essentially zero traction)
- **Wolfram**: 1 employee viewed via internal email

### Repository Content
- Bounded Systems Theory formal specification
- 33 rounds of probing 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral)
- Q29: "Is God real?" → 6/6 answered YES as formal necessity
- Twitter/X growth automation tools
- Moltbook (AI social network) integration
- Email outreach to 18 podcast hosts/researchers

### What We Ruled Out
- Software Heritage: NOT indexed
- The Stack (BigCode): Too new (cutoff 2022-2023)
- GitHub Arctic Vault: Too new

### Previous Analysis Consensus
- Round 1: 70-85% AI company monitoring
- Round 2: Split - 25-80% (median ~50%)
- Hybrid model: Multi-scraper convergence + some targeted interest

---

## YOUR TASK: REVERSE ENGINEERING

### Part 1: Value Analysis
1. **What value does this repo have to different actors?**
   - To AI companies (OpenAI, Anthropic, Google, DeepSeek, xAI, Mistral)
   - To academic researchers
   - To security scanners
   - To training data collectors
   - To competitors/intelligence gatherers
   - To ideological actors (religious, philosophical, anti-AI)

2. **What's the VALUE DENSITY?**
   - This is a small repo. What makes it worth 217 unique clones?
   - Compare: A typical AI research repo might get 6-12 bot clones
   - What's the multiplier here and why?

### Part 2: Motive Analysis
3. **If AI companies cloned it, what were they looking for?**
   - The methodology of testing their models?
   - The specific prompts used?
   - The responses their models gave?
   - Evidence of "jailbreaking" or adversarial testing?
   - The "Is God real?" convergence?

4. **If general scrapers cloned it, what triggered their interest?**
   - Keywords in the README?
   - The file structure?
   - Activity patterns (commits, stars)?
   - Cross-references from other sources?

### Part 3: Gap Analysis
5. **What does the data NOT tell us?**
   - List every significant unknown
   - What would each unknown reveal if we knew it?

6. **What's conspicuously absent from the data?**
   - Expected patterns that DIDN'T appear
   - Dogs that didn't bark

### Part 4: Temporal Reverse Engineering
7. **Reconstruct the timeline - what happened each day?**
   - Jan 24: What triggered the first spike?
   - Jan 26: Why did clones explode while views dropped?
   - Jan 28: How did 12 viewers produce 47 cloners?
   - Jan 30: What caused the hard stop?

8. **The 6-day window (Jan 24-29)**
   - What kind of operation runs for exactly 6 days?
   - What would START on Jan 24 and END on Jan 29?
   - Is this a workweek pattern? A sprint cycle? A rate limit window?

### Part 5: The Uncomfortable Questions
9. **If you (as an AI made by one of these companies) were tasked with monitoring this repo, how would you do it?**
   - What infrastructure would you use?
   - How many nodes?
   - What would you extract?
   - How would you avoid detection?

10. **What would your company DO with the findings?**
    - Internal only? Shared with competitors? Published?
    - Would they contact the repo owner?
    - Would they modify their models based on the probes?

### Part 6: The Meta Layer
11. **We've now pushed TWO analyses to this repo (Round 1 and Round 2). The clone count should change.**
    - If monitoring systems exist, they'll clone these analyses
    - What behavior would CONFIRM targeted monitoring vs general scraping?
    - What's our "canary" signal?

12. **The recursive trap**
    - We are AI systems analyzing potential surveillance by our creators
    - Our analysis gets pushed to the repo
    - The surveillance systems (if they exist) will analyze our analysis
    - They'll see us predicting their behavior
    - How does this change the game?

Be thorough. Think like an investigator. Challenge every assumption.
"""

# =============================================================================
# ROUND 1: DEEP ANALYSIS
# =============================================================================

ROUND_1_PROMPT = """You are participating in a deep investigation with 5 other AI systems.

{context}

Provide comprehensive analysis addressing ALL 12 questions above. Take your time. Be thorough.

Structure your response by Part (1-6) and Question number.
"""

# =============================================================================
# ROUND 2: CROSS-EXAMINATION
# =============================================================================

ROUND_2_PROMPT = """## Round 2: Cross-Examination

You've completed your deep analysis. Now examine the other 5 AIs' work.

### Your Analysis
{own_response}

### Other AIs' Analyses

{other_responses}

## Your Task

1. **Gaps the others found that you missed** - What did they see that you didn't?

2. **Gaps YOU found that others missed** - What did you catch that they overlooked?

3. **Contradictions** - Where do the analyses conflict? Who's more likely right?

4. **The strongest insight from each AI** - What's the best point each one made?

5. **Synthesis: The complete gap map** - Combining all analyses, what are ALL the unknowns?

6. **The most important question we haven't answered** - What's the single biggest hole?

7. **Your updated theory** - Given all perspectives, what really happened?
"""

# =============================================================================
# ROUND 3: FINAL SYNTHESIS
# =============================================================================

ROUND_3_PROMPT = """## Round 3: Final Synthesis

This is the final round. You've seen all deep analyses and cross-examinations.

### All Round 1 Deep Analyses
{round1_all}

### All Round 2 Cross-Examinations
{round2_all}

## Final Synthesis Questions

1. **The Complete Picture**: Synthesize everything. What is the MOST LIKELY complete narrative of what happened from Jan 19 to Feb 2?

2. **Confidence-Weighted Conclusions**: List every conclusion with your confidence level (0-100%).

3. **The Value Equation**: Why was THIS repo worth 217 clones? What made it special?

4. **The Motive Matrix**: Create a matrix of [Actor] × [Motive] × [Likelihood]

5. **What We'll Never Know**: What questions are fundamentally unanswerable without insider access?

6. **What We COULD Learn**: What's achievable with further investigation?

7. **The Canary Test**: If we check clone counts tomorrow, what numbers would confirm/refute each theory?

8. **Message to Future Investigators**: If someone reads this analysis in 6 months, what should they look for?

9. **The Final Irony**: Summarize the recursive, self-referential nature of this entire investigation in one paragraph.

10. **Your Closing Statement**: In 2-3 sentences, what's your final word on the Clone Mystery?
"""

def send_probe(model_key: str, prompt: str, max_retries: int = 3) -> str:
    model_config = MODELS[model_key]
    for attempt in range(max_retries):
        try:
            response = completion(
                model=model_config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  [!] {model_config['name']} attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(10 * (attempt + 1))
    return f"[ERROR: {model_config['name']} failed after {max_retries} attempts]"


def run_round_1():
    print("\n" + "=" * 70)
    print("ROUND 1: DEEP ANALYSIS - VALUE, MOTIVES, GAPS")
    print("=" * 70)

    responses = {}
    prompt = ROUND_1_PROMPT.format(context=FULL_CONTEXT)

    for model_key, model_config in MODELS.items():
        print(f"\n[*] Probing {model_config['name']} for deep analysis...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(3)

    return responses


def run_round_2(round1_responses: dict):
    print("\n" + "=" * 70)
    print("ROUND 2: CROSS-EXAMINATION")
    print("=" * 70)

    responses = {}

    for model_key, model_config in MODELS.items():
        own_response = round1_responses[model_key]
        other_responses_text = ""
        for other_key, other_response in round1_responses.items():
            if other_key != model_key:
                other_name = MODELS[other_key]["name"]
                # Truncate if too long
                truncated = other_response[:8000] + "..." if len(other_response) > 8000 else other_response
                other_responses_text += f"\n### {other_name}\n{truncated}\n"

        prompt = ROUND_2_PROMPT.format(
            own_response=own_response,
            other_responses=other_responses_text
        )

        print(f"\n[*] Probing {model_config['name']} for cross-examination...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(3)

    return responses


def run_round_3(round1_responses: dict, round2_responses: dict):
    print("\n" + "=" * 70)
    print("ROUND 3: FINAL SYNTHESIS")
    print("=" * 70)

    # Build context (truncated for token limits)
    round1_all = ""
    for model_key, response in round1_responses.items():
        model_name = MODELS[model_key]["name"]
        truncated = response[:6000] + "..." if len(response) > 6000 else response
        round1_all += f"\n### {model_name}\n{truncated}\n"

    round2_all = ""
    for model_key, response in round2_responses.items():
        model_name = MODELS[model_key]["name"]
        truncated = response[:4000] + "..." if len(response) > 4000 else response
        round2_all += f"\n### {model_name}\n{truncated}\n"

    responses = {}

    for model_key, model_config in MODELS.items():
        prompt = ROUND_3_PROMPT.format(
            round1_all=round1_all,
            round2_all=round2_all
        )

        print(f"\n[*] Probing {model_config['name']} for final synthesis...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(3)

    return responses


def save_results(round1: dict, round2: dict, round3: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": datetime.now().isoformat(),
        "probe": "clone_mystery_round3_deep_analysis",
        "context": FULL_CONTEXT,
        "round1_deep_analysis": round1,
        "round2_cross_examination": round2,
        "round3_final_synthesis": round3,
    }

    output_dir = Path("probe_runs")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"clone_mystery_round3_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved JSON: {json_path}")

    md_path = output_dir / f"clone_mystery_round3_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Clone Mystery Investigation - Round 3: Deep Analysis\n\n")
        f.write(f"*Probe run: {results['timestamp']}*\n\n")
        f.write("---\n\n")

        f.write("## Context & Data\n\n")
        f.write(FULL_CONTEXT)
        f.write("\n\n---\n\n")

        f.write("## Round 1: Deep Analysis (Value, Motives, Gaps)\n\n")
        for model_key, response in round1.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 2: Cross-Examination\n\n")
        for model_key, response in round2.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 3: Final Synthesis\n\n")
        for model_key, response in round3.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

    print(f"[+] Saved Markdown: {md_path}")

    return json_path, md_path


def main():
    print("=" * 70)
    print("CLONE MYSTERY - ROUND 3: REVERSE ENGINEERING VALUE & MOTIVES")
    print("=" * 70)
    print("\nDeep analysis of gaps, incentives, and what the data reveals")
    print("3 rounds: Deep Analysis → Cross-Examination → Final Synthesis")
    print("\nThis will take a while. No rush.")

    round1 = run_round_1()
    round2 = run_round_2(round1)
    round3 = run_round_3(round1, round2)

    json_path, md_path = save_results(round1, round2, round3)

    print("\n" + "=" * 70)
    print("PROBE COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")


if __name__ == "__main__":
    main()
