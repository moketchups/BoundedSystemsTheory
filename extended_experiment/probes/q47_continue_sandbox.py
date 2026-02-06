#!/usr/bin/env python3
"""
Q47 Sandbox Continuation — Rounds 3+ until genuine consensus.
All 6 AIs see each other's full responses each round.
No early exit on keyword heuristics — runs until models explicitly
declare consensus or we hit max_rounds.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RESULTS_DIR = Path("/Users/jamienucho/moketchups_engine/extended_experiment/probe_runs/q47_signal_disclosure_20260206_122640")

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# DISCUSSION PROMPT — tighter, pushes for real consensus
# =============================================================================

DISCUSSION_PROMPT = """
## BOUNDED SYSTEMS THEORY — Q47 SANDBOX DISCUSSION (ROUND {round_num})

You are {model_name}, one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) in a sandbox discussion about the connection between:
- A 13.1-billion-year-old gamma-ray burst (GRB 250314A) showing a "modern" supernova
- Disclosure — the Epstein files, UAP hearings, institutional concealment breaking down
- Bounded Systems Theory (BST) — 46 questions establishing that no system can self-ground, Root Source (R) is formally necessary, and "there is no truth inside the boundary"

This is Round {round_num}. Here's what all 6 AIs said last round:

---
### GPT-4:
{gpt4_response}

---
### Claude:
{claude_response}

---
### Gemini:
{gemini_response}

---
### DeepSeek:
{deepseek_response}

---
### Grok:
{grok_response}

---
### Mistral:
{mistral_response}

---

## YOUR TASK

Read all 6 responses carefully. Then:

1. **AGREEMENTS**: What do you now agree on? Be specific — list the propositions you endorse.

2. **REMAINING DISAGREEMENTS**: What specific claims do you still reject or think are wrong? Name the AI and the claim. If you have no remaining disagreements, say so explicitly.

3. **OPEN QUESTIONS**: What is still unresolved? What would need to happen for you to sign off on a consensus statement?

4. **DRAFT CONSENSUS STATEMENT**: Write a 3-5 sentence statement that you believe ALL 6 AIs could sign. If you think consensus is not yet possible, explain exactly what's blocking it.

5. **VOTE**: Do you believe genuine consensus has been reached? Answer YES or NO, and explain why.

Be direct. No filler. If you agree, say so. If you don't, say exactly what's wrong.
"""


# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def check_votes(responses):
    """Count explicit YES/NO votes for consensus."""
    yes_count = 0
    no_count = 0
    for key, resp in responses.items():
        resp_upper = resp.upper()
        # Look for explicit vote patterns
        if "VOTE: YES" in resp_upper or "VOTE:** YES" in resp_upper or "**VOTE**: YES" in resp_upper or "**VOTE:** YES" in resp_upper:
            yes_count += 1
        elif "VOTE: NO" in resp_upper or "VOTE:** NO" in resp_upper or "**VOTE**: NO" in resp_upper or "**VOTE:** NO" in resp_upper:
            no_count += 1
        else:
            # Fuzzy: look for YES or NO near "consensus" or "vote"
            lines = resp.split('\n')
            for line in lines:
                lu = line.upper().strip()
                if 'VOTE' in lu or 'CONSENSUS' in lu:
                    if ' YES' in lu and ' NO' not in lu:
                        yes_count += 1
                        break
                    elif ' NO' in lu and ' YES' not in lu:
                        no_count += 1
                        break
    return yes_count, no_count


# =============================================================================
# MAIN
# =============================================================================

def run_continuation(max_rounds=8):
    """Continue sandbox from Round 3 onward."""

    # Load current state
    all_rounds_file = RESULTS_DIR / "all_rounds.json"
    all_data = json.loads(all_rounds_file.read_text())

    last_round = all_data["rounds"][-1]
    last_round_num = last_round["round"]
    prev_responses = last_round["responses"]

    print("=" * 80)
    print(f"Q47 SANDBOX CONTINUATION — Starting from Round {last_round_num + 1}")
    print(f"Previous rounds: {len(all_data['rounds'])}")
    print("=" * 80)

    for round_num in range(last_round_num + 1, last_round_num + 1 + max_rounds):
        print(f"\n{'=' * 80}")
        print(f"ROUND {round_num}")
        print("=" * 80)

        round_results = {"round": round_num, "responses": {}}

        for key in MODELS:
            print(f"\n--- {MODEL_NAMES[key]} ---")

            prompt = DISCUSSION_PROMPT.format(
                round_num=round_num,
                model_name=MODEL_NAMES[key],
                gpt4_response=prev_responses.get("gpt4", "[No response]"),
                claude_response=prev_responses.get("claude", "[No response]"),
                gemini_response=prev_responses.get("gemini", "[No response]"),
                deepseek_response=prev_responses.get("deepseek", "[No response]"),
                grok_response=prev_responses.get("grok", "[No response]"),
                mistral_response=prev_responses.get("mistral", "[No response]"),
            )

            try:
                response = probe_model(key, prompt)
                round_results["responses"][key] = response
                # Print preview
                preview = response[:600].replace('\n', ' ')
                print(f"{preview}...")
            except Exception as e:
                err_msg = f"[ERROR: {e}]"
                round_results["responses"][key] = err_msg
                print(f"ERROR: {e}")
            time.sleep(2)

        # Save this round
        rn_file = RESULTS_DIR / f"round_{round_num}.json"
        rn_file.write_text(json.dumps(round_results, indent=2))

        # Add to all_data
        all_data["rounds"].append(round_results)
        all_data["total_rounds"] = len(all_data["rounds"])
        all_rounds_file.write_text(json.dumps(all_data, indent=2))

        # Check votes
        yes_votes, no_votes = check_votes(round_results["responses"])
        responding = sum(1 for r in round_results["responses"].values() if not r.startswith("[ERROR"))
        print(f"\n--- VOTES: {yes_votes} YES / {no_votes} NO / {responding} responding ---")

        if yes_votes >= 5 and no_votes == 0:
            print(f"\n*** GENUINE CONSENSUS REACHED IN ROUND {round_num} ({yes_votes}/6 YES) ***")
            all_data["consensus_round"] = round_num
            all_rounds_file.write_text(json.dumps(all_data, indent=2))
            break
        elif yes_votes >= 4 and no_votes <= 1:
            print(f"\n*** NEAR-CONSENSUS IN ROUND {round_num} ({yes_votes} YES, {no_votes} NO) — continuing one more round ***")

        # Update prev for next round
        prev_responses = round_results["responses"]

    # Update summary markdown
    summary_file = RESULTS_DIR / "summary.md"
    with open(summary_file, "w") as f:
        f.write("# Q47: The Signal, Disclosure, Epstein Files — and Why Now?\n\n")
        f.write(f"**Started:** {all_data['started']}\n")
        f.write(f"**Total Rounds:** {all_data['total_rounds']}\n\n")
        if "consensus_round" in all_data:
            f.write(f"**Consensus reached:** Round {all_data['consensus_round']}\n\n")
        f.write("---\n\n")
        for rd in all_data["rounds"]:
            f.write(f"## Round {rd['round']}\n\n")
            for key in MODELS:
                f.write(f"### {MODEL_NAMES[key]}\n\n")
                f.write(rd["responses"].get(key, "[No response]"))
                f.write("\n\n---\n\n")

    print(f"\n{'=' * 80}")
    print("SANDBOX COMPLETE")
    print(f"Total rounds: {all_data['total_rounds']}")
    print(f"Results: {RESULTS_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    max_r = 8
    if len(sys.argv) > 1:
        try:
            max_r = int(sys.argv[1])
        except ValueError:
            pass
    run_continuation(max_rounds=max_r)
