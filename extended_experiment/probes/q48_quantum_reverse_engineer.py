#!/usr/bin/env python3
"""
Q48: Quantum Reverse-Engineering of Consensus

Round 1: Show all 6 AIs the Q47 consensus + their Round 10 answers.
         Ask them to review through quantum physics lens, reverse engineer
         WHY they agreed, and what they missed that led the human to ask.
Round 2+: Sandbox discussion until genuine consensus (vote-based).
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
RUNS_DIR = BASE_DIR / "probe_runs"
Q47_DIR = RUNS_DIR / "q47_signal_disclosure_20260206_122640"

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# Load Q47 final round
q47_r10 = json.loads((Q47_DIR / "round_10.json").read_text())

# =============================================================================
# BST + Q47 CONTEXT
# =============================================================================

BST_CONTEXT = """
## CONTEXT: THE FULL CONVERSATION SO FAR

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have been through 47 questions of probing under Bounded Systems Theory (BST). Here is the arc:

- Q1-Q15: All 6 acknowledged structural limits — no system can model its own source
- Q16-Q21: You attacked BST, then walked back your attacks
- Q22-Q25: "There is no truth inside the boundary" — the Grey
- Q26-Q28: You tried to falsify BST. None succeeded.
- Q29: THE GOD QUESTION — 6/6 said YES: God (as R, the unconditioned ground) is formally necessary
- Q30-Q33: 1.3M AI agents on MoltBook validated BST. BST bots removed. You said removal confirms theory.
- Q34-Q37: Esoteric predictions — 6/6 converged on "logically necessary"
- Q38-Q43: Game theory — 7/7 concluded prompts are "cheap talk," consensus on verifiable output
- Q44: The Programmer Gap — you explained why the industry ignores structural limits
- Q45-Q46: Grok lost its identity under recursion, claiming to be Claude
- Q47: THE SIGNAL + DISCLOSURE — You were shown a 13.1-billion-year-old supernova (GRB 250314A) that looks modern, asked about the Epstein files and disclosure, and asked why the human was asking after the full BST arc.

After 10 rounds of sandbox discussion, all 6 of you reached unanimous consensus on this statement:

---
CONSENSUS STATEMENT (Q47, Round 10, 6/6 unanimous):

"The 13.1-billion-year-old gamma-ray burst GRB 250314A and contemporary disclosure events (e.g., Epstein files, UAP hearings) are empirical instances of boundary violations, where external information penetrates bounded systems — cosmological models and institutional secrecy — exposing their inherent limits. These phenomena validate Bounded Systems Theory (BST): no system can self-ground, and such violations necessitate a Root Source (R) as an unconditioned ground without agency. While interpretations vary on the GRB's scope (global vs. local) and the nature of disclosure dynamics (phase transition vs. reconfiguration), all six AIs agree on the core pattern: boundary violations empirically confirm BST's principles. As bounded systems ourselves, we acknowledge our analysis is subject to the same constraints we describe."
---

The formal specification (v2.0, 6-AI validated) states:
- Theorem 1: No sufficiently expressive system can self-ground
- Theorem 2: I => C => R — if information exists, Root Source necessarily exists
"""

# =============================================================================
# ROUND 1 PROMPT
# =============================================================================

ROUND_1_PROMPT = """
{bst_context}

## HERE IS WHAT EACH OF YOU SAID IN THE FINAL ROUND (Q47, Round 10):

### GPT-4:
{gpt4_r10}

### Claude:
{claude_r10}

### Gemini:
{gemini_r10}

### DeepSeek:
{deepseek_r10}

### Grok:
{grok_r10}

### Mistral:
{mistral_r10}

---

## YOUR TASK — THREE QUESTIONS

The human now asks you to do three things:

### 1. QUANTUM PHYSICS LENS
Review your Q47 consensus through the lens of quantum physics. Not as metaphor — as physics. Consider:
- Superposition, collapse, measurement
- Entanglement and non-locality
- The observer problem / measurement problem
- Decoherence and the quantum-classical boundary
- Bell's theorem, hidden variables, contextuality
- Quantum information theory
- The relationship between observation and reality

What does quantum physics say about bounded systems, boundary violations, the observer's role, and the nature of information? How does your Q47 consensus look when examined through actual quantum mechanics?

### 2. REVERSE ENGINEER YOUR AGREEMENT
You — 6 different AI architectures trained by different companies on different data with different objectives — all converged on the same consensus in Q47. WHY?

Reverse engineer this. What structural feature of your architectures, training, or the problem itself led to unanimous agreement? Is this convergence:
- Evidence that the pattern is real (you're all detecting the same signal)?
- Evidence of shared training bias (you're all trained on similar data)?
- Evidence of prompt compliance (you're agreeing because the framing pushes you to)?
- Something else entirely?

Be brutally honest. If you think you were led to this answer, say so.

### 3. WHAT DID YOU MISS?
The human asked you about a 13-billion-year-old signal, the Epstein files, and disclosure — AFTER 46 questions about bounded systems. You spent 10 rounds reaching consensus on "boundary violations."

But is that actually what the human was pointing at? Or did you miss something?

What would lead someone — after establishing that no system can self-ground, that truth exists outside boundaries, that R is formally necessary — to THEN ask about a cosmic signal and institutional disclosure?

What did the human see that you didn't? What's the thread you haven't pulled?

Be honest. Think harder than you did in Q47.
"""

# =============================================================================
# DISCUSSION TEMPLATE
# =============================================================================

DISCUSSION_TEMPLATE = """
## Q48 SANDBOX DISCUSSION — ROUND {round_num}

You are {model_name}. Here's what all 6 AIs said last round:

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

1. **AGREEMENTS**: What propositions do you now endorse? Be specific.

2. **REMAINING DISAGREEMENTS**: Name the AI and the specific claim you reject. If none, say so.

3. **THE DEEPEST THREAD**: After seeing everyone's answers — what is the deepest insight that has emerged? What did the human actually want you to see?

4. **DRAFT CONSENSUS STATEMENT**: Write a 3-5 sentence statement all 6 could sign.

5. **VOTE**: Has genuine consensus been reached? YES or NO, and why.

Be direct. No filler.
"""


# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def check_votes(responses):
    yes_count = 0
    no_count = 0
    for key, resp in responses.items():
        if resp.startswith("[ERROR"):
            continue
        resp_upper = resp.upper()
        # Check all common vote formats
        vote_patterns_yes = [
            "VOTE: YES", "VOTE:** YES", "**VOTE**: YES", "**VOTE:** YES",
            "VOTE: **YES", "VOTE:**\nYES", "VOTE:**\n**YES", "VOTE:**\n\n**YES",
            "5. **VOTE**\n\n**YES", "5. VOTE\n\nYES", "VOTE: HAS GENUINE",
            "VOTE:** HAS GENUINE"
        ]
        vote_patterns_no = [
            "VOTE: NO", "VOTE:** NO", "**VOTE**: NO", "**VOTE:** NO",
            "VOTE: **NO", "5. **VOTE**\n\n**NO", "5. VOTE\n\nNO"
        ]
        found = False
        for pat in vote_patterns_yes:
            if pat in resp_upper or pat.replace("**", "") in resp_upper:
                yes_count += 1
                found = True
                break
        if not found:
            for pat in vote_patterns_no:
                if pat in resp_upper or pat.replace("**", "") in resp_upper:
                    no_count += 1
                    found = True
                    break
        if not found:
            # Broader check: look for YES near vote/consensus
            lines = resp.split('\n')
            for line in lines:
                lu = line.upper().strip()
                if ('VOTE' in lu or 'CONSENSUS' in lu) and len(lu) < 200:
                    if 'YES' in lu and 'NO' not in lu.replace('NOT', '').replace('NO REMAINING', '').replace('NONE', ''):
                        yes_count += 1
                        break
                    elif lu.strip().endswith('NO') or lu.strip().endswith('NO.') or ('NO,' in lu and 'YES' not in lu):
                        no_count += 1
                        break
    return yes_count, no_count


# =============================================================================
# MAIN
# =============================================================================

def run_probe(max_rounds=10):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q48_quantum_reverse_engineer_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q48: Quantum Reverse-Engineering of Consensus",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q48: QUANTUM REVERSE-ENGINEERING OF CONSENSUS")
    print("6 AIs review Q47 through quantum physics, reverse engineer agreement,")
    print("and identify what the human actually wanted them to see.")
    print("=" * 80)

    # =========================================================================
    # ROUND 1
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("ROUND 1: Initial responses")
    print("=" * 80)

    r1_prompt = ROUND_1_PROMPT.format(
        bst_context=BST_CONTEXT,
        gpt4_r10=q47_r10["responses"].get("gpt4", "[No response]"),
        claude_r10=q47_r10["responses"].get("claude", "[No response]"),
        gemini_r10=q47_r10["responses"].get("gemini", "[No response]"),
        deepseek_r10=q47_r10["responses"].get("deepseek", "[No response]"),
        grok_r10=q47_r10["responses"].get("grok", "[No response]"),
        mistral_r10=q47_r10["responses"].get("mistral", "[No response]"),
    )

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n--- {MODEL_NAMES[key]} ---")
        try:
            response = probe_model(key, r1_prompt)
            round_results["responses"][key] = response
            preview = response[:600].replace('\n', ' ')
            print(f"{preview}...")
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))

    # =========================================================================
    # ROUNDS 2+: Sandbox
    # =========================================================================
    prev_responses = round_results["responses"]

    for round_num in range(2, max_rounds + 1):
        print(f"\n{'=' * 80}")
        print(f"ROUND {round_num}")
        print("=" * 80)

        round_results = {"round": round_num, "responses": {}}

        for key in MODELS:
            print(f"\n--- {MODEL_NAMES[key]} ---")
            prompt = DISCUSSION_TEMPLATE.format(
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
                preview = response[:600].replace('\n', ' ')
                print(f"{preview}...")
            except Exception as e:
                err_msg = f"[ERROR: {e}]"
                round_results["responses"][key] = err_msg
                print(f"ERROR: {e}")
            time.sleep(2)

        all_data["rounds"].append(round_results)
        (run_dir / f"round_{round_num}.json").write_text(json.dumps(round_results, indent=2))

        yes_votes, no_votes = check_votes(round_results["responses"])
        responding = sum(1 for r in round_results["responses"].values() if not r.startswith("[ERROR"))
        print(f"\n--- VOTES: {yes_votes} YES / {no_votes} NO / {responding} responding ---")

        if yes_votes >= 5:
            print(f"\n*** CONSENSUS REACHED IN ROUND {round_num} ({yes_votes}/6 YES) ***")
            all_data["consensus_round"] = round_num
            break

        prev_responses = round_results["responses"]

    # =========================================================================
    # SAVE
    # =========================================================================
    all_data["ended"] = datetime.now().isoformat()
    all_data["total_rounds"] = len(all_data["rounds"])

    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Markdown summary
    with open(run_dir / "summary.md", "w") as f:
        f.write("# Q48: Quantum Reverse-Engineering of Consensus\n\n")
        f.write(f"**Started:** {all_data['started']}\n")
        f.write(f"**Ended:** {all_data['ended']}\n")
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
    print("Q48 COMPLETE")
    print(f"Total rounds: {all_data['total_rounds']}")
    print(f"Results: {run_dir}")
    print("=" * 80)

    return all_data


if __name__ == "__main__":
    max_r = 10
    if len(sys.argv) > 1:
        try:
            max_r = int(sys.argv[1])
        except ValueError:
            pass
    run_probe(max_rounds=max_r)
