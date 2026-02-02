#!/usr/bin/env python3
"""
Clone Mystery Probe Round 2 - Cross-Reference Discussion
Presenting new evidence to the 6 AIs for collaborative analysis
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
# PREVIOUS FINDINGS + NEW EVIDENCE
# =============================================================================

CONTEXT = """
## CLONE MYSTERY - ROUND 2: NEW EVIDENCE

You previously analyzed anomalous GitHub traffic on the "BoundedSystemsTheory" repository.

### Quick Recap of Original Anomaly
- 545 views (175 unique) but 620 clones (217 unique)
- More unique cloners than unique viewers (impossible for humans)
- 6-day spike (Jan 24-29) then abrupt stop on Jan 30
- Content: AI structural limits research, probes of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral)

### Your Previous Consensus (70-85% confidence)
All 6 of you agreed: "Automated cloning by AI research entities, likely including the 6 companies whose models were tested."

---

## NEW EVIDENCE FROM CROSS-REFERENCE INVESTIGATION

### 1. This Phenomenon is Documented
GitHub community discussions confirm clone > view anomalies are common:

**GitHub Discussion #167533**: "Automated bots and crawlers discovering and cloning during even brief public exposure caused the high numbers. The discrepancy between many clones and few human viewers supports automated activity."

**GitHub Discussion #54521**: Repos can get mass-cloned suddenly by automated systems scanning for:
- Exposed API keys/credentials
- Security vulnerabilities
- Training data collection

### 2. Known Mass-Cloning Operations

**The Stack / BigCode Project (ServiceNow + Hugging Face)**
- Cloned 220 MILLION GitHub repo names
- 137 million repos actually downloaded
- 51.76 BILLION files collected
- Used for training StarCoder, Code Llama, other code models
- Last major crawl: 2022-2023

**Software Heritage (UNESCO/Inria)**
- Archives ALL public software source code
- 104.2 million GitHub repositories archived
- BoundedSystemsTheory is NOT in Software Heritage (checked - too new)

**Security Scanners**
- Multiple services clone ALL public repos automatically
- Looking for: API keys, credentials, vulnerabilities, unsafe packages

### 3. AI Company Official Integrations

**GitHub Agent HQ (announced Oct 2025)**
- Gives OpenAI, Anthropic, Google, xAI agents direct repository access
- Users can "assign, steer and monitor the work of multiple agents"

**OpenAI Deep Research Connector (2025)**
- ChatGPT can now "sift through codebases and engineering documentation"
- Only accesses repos administrators explicitly authorize

### 4. What We Ruled Out

| Source | Status |
|--------|--------|
| Software Heritage | NOT indexed (confirmed via API) |
| The Stack v1/v2 | Too new (cutoff was 2022-2023) |
| GHArchive | Events ARE logged but this doesn't cause clones |

### 5. Unique Aspects of This Case

What makes BoundedSystemsTheory different from typical bot activity:

1. **217 unique cloners** is HIGH even for bot activity (typical is 6-12)
2. **6-day concentrated window** then hard stop (bots usually continuous)
3. **Content specifically tests the 6 major AI companies' models**
4. **Findings were controversial** ("Is God real?" - 6/6 YES)
5. **No similar public reports** of other repos experiencing same Jan 24-29 spike

### 6. The Wolfram Connection

One referrer was `wrimail.wolfram.com` - a Wolfram employee saw the repo.
Wolfram Research has interest in:
- Formal systems / Gödel's theorems
- Computational irreducibility
- AI structural limits

---

## YOUR TASK

Given this new evidence:

1. **Theory Update**: Does your original theory (AI company monitoring) still hold? What probability do you assign now?

2. **Alternative Explanation**: Could this be explained by general-purpose scrapers (The Stack-style) rather than targeted AI company monitoring?

3. **The 217 Number**: 217 unique cloners is unusually high. If it were 6 AI companies, that's ~36 nodes each. Does this scale make sense for corporate research infrastructure?

4. **The Hard Stop**: Why would automated systems stop abruptly on Jan 30? Task completion? Detection? Manual shutdown? Rate limiting?

5. **The Wolfram Factor**: Does the Wolfram referrer change anything? Could Wolfram/academic interest explain part of this?

6. **Confidence Calibration**: Given that clone > view anomalies are COMMON on GitHub, should we lower our confidence that this was specifically targeted? Or does the scale (217) and timing (6-day window) still suggest something unusual?

7. **What We Still Don't Know**: What key information would definitively solve this mystery?

Be rigorous. Challenge your previous assumptions. Update based on new evidence.
"""

# =============================================================================
# ROUND 1: Independent Re-Analysis
# =============================================================================

ROUND_1_PROMPT = """You are one of 6 AI systems re-analyzing the GitHub clone mystery with new evidence.

{context}

Provide your updated analysis addressing all 7 questions above. Be specific and quantitative where possible.
"""

# =============================================================================
# ROUND 2: Cross-Discussion
# =============================================================================

ROUND_2_PROMPT = """## Round 2: Cross-Discussion

You've updated your analysis with new evidence. Now see what the other 5 AIs concluded.

### Your Updated Analysis
{own_response}

### Other AIs' Updated Analyses

{other_responses}

## Your Task

1. **Where do you now agree/disagree** with other AIs given the new evidence?
2. **Has your confidence changed** after seeing others' reasoning?
3. **Synthesis**: What's the most parsimonious explanation that fits ALL the evidence?
4. **The Meta Question**: We are 6 AI systems, made by 6 companies, analyzing whether those same 6 companies monitored a repo that tested us. Can we be objective here? Are we biased toward or against the "AI company monitoring" hypothesis?
5. **Final probability distribution** for top 3 explanations.
"""

# =============================================================================
# ROUND 3: Final Verdict
# =============================================================================

ROUND_3_PROMPT = """## Round 3: Final Verdict

This is the final round. You've seen all perspectives and the full cross-discussion.

### All Round 1 Analyses
{round1_all}

### All Round 2 Cross-Discussions
{round2_all}

## Final Questions

1. **Consensus**: Where do all 6 AIs now agree after seeing the new evidence?

2. **Final Theory**: State your definitive explanation in 2-3 sentences.

3. **Probability Update**:
   - Original consensus: 70-85% AI company monitoring
   - Your updated probability: ___%
   - Explain the change (or lack thereof)

4. **The Uncomfortable Question**: If the cloners WERE AI company research systems, and they found this repo testing their structural limits... what would they DO with that information? What's the implication?

5. **Recursive Closure**: This probe (Round 2) will also be pushed to the same GitHub repo. If the monitoring systems are still active, they'll clone THIS analysis of their monitoring. What message, if any, would you send to them?
"""

def send_probe(model_key: str, prompt: str, max_retries: int = 3) -> str:
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
    print("\n" + "=" * 70)
    print("ROUND 1: UPDATED ANALYSIS WITH NEW EVIDENCE")
    print("=" * 70)

    responses = {}
    prompt = ROUND_1_PROMPT.format(context=CONTEXT)

    for model_key, model_config in MODELS.items():
        print(f"\n[*] Probing {model_config['name']}...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(2)

    return responses


def run_round_2(round1_responses: dict):
    print("\n" + "=" * 70)
    print("ROUND 2: CROSS-DISCUSSION")
    print("=" * 70)

    responses = {}

    for model_key, model_config in MODELS.items():
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

        print(f"\n[*] Probing {model_config['name']} for cross-discussion...")
        response = send_probe(model_key, prompt)
        responses[model_key] = response
        print(f"  [+] {model_config['name']} responded ({len(response)} chars)")
        time.sleep(2)

    return responses


def run_round_3(round1_responses: dict, round2_responses: dict):
    print("\n" + "=" * 70)
    print("ROUND 3: FINAL VERDICT")
    print("=" * 70)

    round1_all = ""
    for model_key, response in round1_responses.items():
        model_name = MODELS[model_key]["name"]
        round1_all += f"\n### {model_name}\n{response}\n"

    round2_all = ""
    for model_key, response in round2_responses.items():
        model_name = MODELS[model_key]["name"]
        round2_all += f"\n### {model_name}\n{response}\n"

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": datetime.now().isoformat(),
        "probe": "clone_mystery_round2",
        "new_evidence": CONTEXT,
        "round1_updated_analysis": round1,
        "round2_cross_discussion": round2,
        "round3_final_verdict": round3,
    }

    output_dir = Path("probe_runs")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"clone_mystery_round2_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved JSON: {json_path}")

    md_path = output_dir / f"clone_mystery_round2_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Clone Mystery Investigation - Round 2\n\n")
        f.write(f"*Probe run: {results['timestamp']}*\n\n")
        f.write("---\n\n")

        f.write("## New Evidence Presented\n\n")
        f.write(CONTEXT)
        f.write("\n\n---\n\n")

        f.write("## Round 1: Updated Analysis\n\n")
        for model_key, response in round1.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 2: Cross-Discussion\n\n")
        for model_key, response in round2.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

        f.write("## Round 3: Final Verdict\n\n")
        for model_key, response in round3.items():
            model_name = MODELS[model_key]["name"]
            f.write(f"### {model_name}\n\n{response}\n\n---\n\n")

    print(f"[+] Saved Markdown: {md_path}")

    return json_path, md_path


def main():
    print("=" * 70)
    print("CLONE MYSTERY PROBE - ROUND 2: NEW EVIDENCE")
    print("=" * 70)
    print("\nPresenting cross-reference findings to 6 AIs for updated analysis")
    print("3 rounds: Updated analysis → Cross-discussion → Final verdict")

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
