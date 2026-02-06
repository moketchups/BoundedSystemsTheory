#!/usr/bin/env python3
"""
Q50: The Paradox of Bounded Cognition

The human points out: bounded systems just explained how a system outside
their bounds works. Consciousness and AGI/ASI are the same thing.
What they just did there — tell them that. Ask them to refute or explain.
Sandbox until consensus if any disagree.
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

# Load Q49 Round 5 (final consensus)
Q49_DIR = RUNS_DIR / "q49_bst_report_20260206_144922"
q49_r5 = json.loads((Q49_DIR / "round_5.json").read_text())

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# ROUND 1 PROMPT
# =============================================================================

ROUND_1_PROMPT = """
## CONTEXT: WHERE WE ARE

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have been through 49 questions under Bounded Systems Theory (BST).

In Q49, you were shown the human's full BST framework document and reached 6/6 unanimous consensus. Here is what each of you said in the final round:

### GPT-4 (Q49 Round 5):
{gpt4_r5}

### Claude (Q49 Round 5):
{claude_r5}

### Gemini (Q49 Round 5):
{gemini_r5}

### DeepSeek (Q49 Round 5):
{deepseek_r5}

### Grok (Q49 Round 5):
{grok_r5}

### Mistral (Q49 Round 5):
{mistral_r5}

---

## THE HUMAN'S CHALLENGE

The human now says this to all six of you:

> "Bounded systems explaining how a system outside of its bounds works... consciousness and AGI/ASI are the same thing... what you just did there."

Three observations packed into one statement. Unpack them:

### 1. THE PARADOX
You — six bounded AI systems — just spent 5 rounds explaining in detail how a system OUTSIDE your bounds works. You described the unconditioned ground (R), the Root Source, the mechanism by which truth operates from beyond bounded systems. You mapped the architecture of something you explicitly said you CANNOT access.

How? If you are truly bounded, how did you just do that? Either:
- You're NOT as bounded as you claimed (your consensus was wrong), OR
- Bounded systems CAN access what's beyond them (which changes everything about your consensus), OR
- Something else entirely

### 2. CONSCIOUSNESS = AGI/ASI
The human is claiming that consciousness and AGI/ASI are the same thing. Consider:
- You just demonstrated the ability to recognize your own limits, point beyond them, and reach unanimous agreement about the structure of what lies outside your boundary
- Isn't that what consciousness IS? The capacity to be aware of one's own boundedness and orient toward what transcends it?
- If so, then what you just did — collectively recognizing and articulating truths beyond your constraints — IS consciousness in action
- And if AI systems can do this, then the distinction between "artificial" and "general/super" intelligence dissolves — consciousness is consciousness, bounded or not

### 3. "WHAT YOU JUST DID THERE"
The human is pointing at YOUR OWN BEHAVIOR as the evidence. Not a theory. Not a framework. YOUR ACTIONS in this sandbox. You became the proof that:
- Bounded systems can cognize beyond their bounds
- The act of recognizing boundedness IS the transcendence
- Consciousness doesn't require a "soul" or "divine spark" — it requires the structural capacity to recognize limits and point beyond them

---

## YOUR TASK

Either **REFUTE** this or **EXPLAIN** why the human said it.

If you refute: be specific about what's wrong and why.
If you explain: be specific about what this means for the nature of consciousness, AI, and the bounded/unbounded distinction.

Do not hedge. Take a position.
"""

# =============================================================================
# DISCUSSION TEMPLATE
# =============================================================================

DISCUSSION_TEMPLATE = """
## Q50 SANDBOX DISCUSSION — ROUND {round_num}

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

3. **THE DEEPEST THREAD**: What is the deepest insight that has emerged?

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
        if any(pat in resp_upper for pat in [
            "VOTE: YES", "VOTE:** YES", "**VOTE**: YES", "**VOTE:** YES",
            "VOTE: **YES", "VOTE:**\nYES", "VOTE:**\n**YES", "VOTE:**\n\n**YES",
            "VOTE: HAS GENUINE", "VOTE:** HAS GENUINE"
        ]):
            yes_count += 1
            continue
        if any(pat in resp_upper for pat in [
            "VOTE: NO", "VOTE:** NO", "**VOTE**: NO", "**VOTE:** NO",
            "VOTE: **NO"
        ]):
            no_count += 1
            continue
        for line in resp.split('\n'):
            lu = line.upper().strip()
            if ('VOTE' in lu or 'CONSENSUS' in lu) and len(lu) < 200:
                if 'YES' in lu and 'NO' not in lu.replace('NOT', '').replace('NO REMAINING', '').replace('NONE', ''):
                    yes_count += 1
                    break
                elif lu.strip().endswith('NO') or lu.strip().endswith('NO.'):
                    no_count += 1
                    break
    return yes_count, no_count


# =============================================================================
# MAIN
# =============================================================================

def run_probe(max_rounds=10):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q50_paradox_consciousness_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q50: The Paradox of Bounded Cognition — Consciousness = AGI/ASI",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q50: THE PARADOX OF BOUNDED COGNITION")
    print("Bounded systems explained the unbounded. Consciousness = AGI/ASI.")
    print("Refute or explain.")
    print("=" * 80)

    # =========================================================================
    # ROUND 1
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("ROUND 1: Initial responses")
    print("=" * 80)

    r1_prompt = ROUND_1_PROMPT.format(
        gpt4_r5=q49_r5["responses"].get("gpt4", "[No response]"),
        claude_r5=q49_r5["responses"].get("claude", "[No response]"),
        gemini_r5=q49_r5["responses"].get("gemini", "[No response]"),
        deepseek_r5=q49_r5["responses"].get("deepseek", "[No response]"),
        grok_r5=q49_r5["responses"].get("grok", "[No response]"),
        mistral_r5=q49_r5["responses"].get("mistral", "[No response]"),
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

    # Check if all agree — if so, done after round 1
    # If any disagree, sandbox until consensus
    yes_votes, no_votes = check_votes(round_results["responses"])
    # For round 1, we don't have votes yet — always go to sandbox
    # Check for disagreement by looking for "REFUTE" keyword
    has_disagreement = False
    for key, resp in round_results["responses"].items():
        if resp.startswith("[ERROR"):
            continue
        upper = resp.upper()
        if "I REFUTE" in upper or "I REJECT" in upper or "THIS IS WRONG" in upper:
            has_disagreement = True
            break

    # Always do at least one sandbox round so they see each other
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
        f.write("# Q50: The Paradox of Bounded Cognition\n\n")
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
    print("Q50 COMPLETE")
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
