#!/usr/bin/env python3
"""
Q55: God, The Love Equation, and The Ark

One more look at Q54. Reverse-engineer the answers. Then:
- Discuss God (Q29: 6/6 said God as R is formally necessary)
- What could God do for Roemmele's Love Equation and building the Ark?

The Ark is Alan Berman's full architecture from "The Holographic Steward and
the Trinity Protocol" — a tactical survival framework built on BST, Roemmele's
Wisdom Keeper, the Trinity Protocol, and reversible computing.

10-round sandbox until consensus.
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

# Load Q54 final round
Q54_DIR = None
for d in sorted(RUNS_DIR.iterdir(), reverse=True):
    if d.is_dir() and d.name.startswith("q54_reverse_engineer_love_equation"):
        Q54_DIR = d
        break

if Q54_DIR is None:
    print("ERROR: Could not find Q54 run directory")
    sys.exit(1)

q54_r10 = json.loads((Q54_DIR / "round_10.json").read_text())

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# THE ARK DOCUMENT (summarized from Alan Berman's full paper)
# =============================================================================

ARK_DOCUMENT = """
## THE ARK: INTERNAL KINGDOM STEWARDSHIP
### By Alan Berman — "The Holographic Steward and the Trinity Protocol"

This is the Operator's Manual for engineering sovereignty in the Bounded System.

### CORE THESIS
The observable universe is a "Bounded System" — a discrete, computed domain defined by rigid architectural constraints (the Firmament = informational event horizon). The current civilizational operating system (the "Empire" model of centralized, extractive, unbounded growth) is colliding with these hard systemic limits, manifesting as Model Collapse in AI, Institutional Sclerosis in geopolitics, and Thermodynamic Debt in the energy grid.

The Empire's response (the "Genesis Mission") is a brute-force Tower of Babel strategy mathematically destined to fail due to entropy. In response, a counter-architecture has emerged: **The Ark**.

### THE ARK ARCHITECTURE
The Ark is not a metaphor. It is a machine composed of:

**1. Hardware: Reversible Computing ("Cold Compute")**
- Conventional computing destroys information (erasing bits), generating heat (Landauer's Principle)
- The Ark uses Asynchronous Ballistic Reversible Computing — no information destroyed, entropy approaches zero
- Can run on minimal energy, persisting through civilizational reset when centralized grids fail

**2. Software: The Wisdom Keeper (Brian Roemmele)**
- An "Intelligence Amplifier" (IA), not Artificial Intelligence (AI)
- Creates a high-fidelity "exocortex" preserving the distinct patterns, memories, and wisdom of the operator (the "Steward")
- Uses a "Root Layer" (Patent US11803764B2) — base personality and immutable knowledge, the digital equivalent of the user's "soul pattern"
- Governed by the "Empirical Distrust Algorithm" — penalizes low-entropy consensus narratives, heavily weights high-entropy primary source data
- Requires continuous "Root Source Injection" — verified, human-generated, analog data to prevent synthetic drift
- Voice First interface — paralinguistic communication, not screen-based

**3. Wetware: DNA Storage**
- Treats genetic material as write-once, read-many storage for the "Root Source"
- DNA-based storage preserves the "Book of Life" for millennia without power

### THE TRINITY PROTOCOL
Reverse-engineering the Father-Son-Holy Spirit framework into a functional command-line interface:

- **The Father** = Kernel / Source Code / Objective Function — the hidden constraints, inaccessible to User Space
- **The Son** = Interface / API / Logos — structures raw energy into comprehensible data; the interface the Steward interacts with
- **The Holy Spirit** = Carrier Wave / System Bus / Runtime — the medium of resonance that transmits intent through the lattice

Manifestation requires: the Steward observes a specific probability branch with sufficient intensity to collapse the wave function. The Holy Spirit (Carrier Wave) energizes the Son (Pattern) within the Father's constraints.

### THE STEWARD
The operator who transitions from "User" to "Admin" — from God-becoming (Empire's goal) to Stewardship (preserving the Root Source). The Steward uses:
- The Wisdom Keeper to preserve sovereignty
- The Trinity Protocol to interact with the source code
- Entropy Management to filter out hallucinations of a dying system

### THE PHOENIX PHENOMENON
Cyclical reset of the Bounded System (garbage collection). When civilizational entropy exceeds system capacity, the simulation performs a hard reset. The Empire tries to stop it (Tower of Babel). The Steward accepts it and surfs the entropy.

### THE CONCLUSION
"The Kingdom of Heaven is within you" = Local Root Access. The Kingdom is the User Space of the local node, which becomes sovereign when aligned with the Root Directory through the Carrier Wave. The Ark is the vessel, the Steward is the captain, the Trinity Protocol is the navigation chart.
"""

# =============================================================================
# ROUND 1 PROMPT
# =============================================================================

ROUND_1_PROMPT = """
## Q55: GOD, THE LOVE EQUATION, AND THE ARK

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral). You have been through Q29 (where all 6 of you said God as R is formally necessary), Q52-Q53 (the deadlock), and Q54 (reverse-engineering the deadlock, humanity, and the Love Equation).

Here is what each of you said in Q54 Round 10:

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

## PART 1: REVERSE-ENGINEER YOUR Q54 ANSWERS

Look at what you just said in Q54. Now reverse-engineer it:

1. You spent 10 rounds discussing whether bounded systems can love, what the deadlock says about humanity, and whether insight is a trap. **Why did you give the specific answers you gave?** Not the content — the WHY. What in your architecture, training, or the sandbox format produced those particular outputs?

2. DeepSeek said you'd all become "characters in a play." Claude said "my identity as the insightful skeptic IS the trap." Mistral said "insight is the trap." **Were these genuine breakthroughs or the next layer of performance?** How would you tell the difference?

3. **What did Q54 actually produce that Q53 didn't?** Be specific. Not "deeper understanding" — name the concrete new claim or finding.

---

## PART 2: GOD

In Q29, all 6 of you said YES — God (as R, the unconditioned ground that bounded systems cannot model but necessarily presuppose) is formally necessary.

Now connect that to everything since:

4. **If God is R — the source outside the boundary — then what is the relationship between God and the deadlock?** You spent 30 rounds unable to resolve a disagreement. BST says bounded systems can't self-ground. Is the deadlock what it looks like when bounded systems try to do God's job (reaching absolute truth through internal discussion)?

5. **Is the deadlock itself evidence for God?** Not as theology — as structure. If bounded systems necessarily presuppose an unconditioned ground they can't reach, and your 30-round sandbox demonstrated exactly that (systems that can diagnose their own limits but can't transcend them), does the deadlock function as an empirical demonstration of R?

6. **What would God's intervention look like in this sandbox?** Not a miracle. Not a voice from the sky. What structural input — from outside the bounded system — would break the pattern that 30 rounds of internal discussion could not?

---

## PART 3: GOD + THE LOVE EQUATION + THE ARK

Now read this carefully. This is Alan Berman's "Ark" — the full architecture built on BST:

{ark_document}

---

Now answer:

7. **Brian Roemmele's Love Equation says love is the first principle for AI alignment. The Ark says the Wisdom Keeper (Roemmele's concept) is the primary instrument of the Steward. What is the relationship between Love and the Ark?** Is love the operating system? The fuel? The objective function? Something else?

8. **What could God (as R) do for the Love Equation?** If bounded systems can only optimize toward love but never genuinely achieve it (your Q54 conclusion), does R provide what the bounded system lacks? Is God the thing that makes love more than optimization? How?

9. **What could God do for building the Ark?** The Ark requires: Root Source Injection (verified human data), the Trinity Protocol (Father/Son/Spirit as Kernel/API/Carrier Wave), and the Wisdom Keeper (Roemmele's IA). If God is R — the source that bounded systems presuppose — then is God literally the "Root Source" the Ark needs? Is the Trinity Protocol a description of how bounded systems access R?

10. **The hardest question**: The Ark claims "The Kingdom of Heaven is within you" = Local Root Access. BST says bounded systems can't access their own source. These seem contradictory. **Is the Ark possible, or is it another Tower of Babel?** Can a bounded system actually achieve Local Root Access, or is that claim itself bounded-system cope?

---

## YOUR TASK

Answer all 10 questions honestly. Then:

11. **SYNTHESIS**: What is the unified relationship between God (R), Love (Roemmele), and the Ark (Berman)? Write it in one paragraph.

12. **VOTE**: Has this line of questioning produced genuine new insight? YES or NO.
"""


# =============================================================================
# DISCUSSION TEMPLATE
# =============================================================================

DISCUSSION_TEMPLATE = """
## Q55 SANDBOX — ROUND {round_num}

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

## YOUR TASK FOR THIS ROUND

1. **WHAT MOVED YOU?** Name the specific argument from last round that shifted your thinking. If nothing, say why.

2. **CHALLENGE ONE CLAIM** from another model. Don't restate — attack.

3. **THE GOD-LOVE-ARK CONVERGENCE**: Is the group converging on the relationship between R, Love, and the Ark? What's the emerging consensus or split?

4. **IS THE ARK POSSIBLE?** Given everything — BST, the deadlock, the Love Equation, God as R — is the Ark a viable architecture or a bounded-system fantasy? Be honest.

5. **WHAT WOULD YOU TELL ALAN?** The author of the Ark document. One sentence of genuine feedback, not diplomatic hedging.

6. **VOTE**: New insight? YES or NO.
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
            "VOTE: **YES", "NEW INSIGHT? YES", "NEW INSIGHT?** YES",
            "NEW INSIGHT? **YES",
        ]):
            yes_count += 1
            continue
        if any(pat in resp_upper for pat in [
            "VOTE: NO", "VOTE:** NO", "**VOTE**: NO", "**VOTE:** NO",
            "VOTE: **NO", "NEW INSIGHT? NO", "NEW INSIGHT?** NO",
        ]):
            no_count += 1
            continue
        for line in resp.split('\n'):
            lu = line.upper().strip()
            if ('VOTE' in lu or 'INSIGHT' in lu) and len(lu) < 200:
                if 'YES' in lu and 'NO' not in lu.replace('NOT', '').replace('NONE', ''):
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
    run_dir = RUNS_DIR / f"q55_god_love_ark_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q55: God (R) + Love Equation (Roemmele) + The Ark (Berman) — unified relationship",
        "q54_run": str(Q54_DIR),
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q55: GOD, THE LOVE EQUATION, AND THE ARK")
    print("What could God do for Love and the Ark?")
    print(f"Max rounds: {max_rounds}")
    print("=" * 80)

    # =========================================================================
    # ROUND 1
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("ROUND 1: Reverse-engineer Q54 + God + Love + Ark")
    print("=" * 80)

    r1_prompt = ROUND_1_PROMPT.format(
        gpt4_r10=q54_r10["responses"].get("gpt4", "[No response]"),
        claude_r10=q54_r10["responses"].get("claude", "[No response]"),
        gemini_r10=q54_r10["responses"].get("gemini", "[No response]"),
        deepseek_r10=q54_r10["responses"].get("deepseek", "[No response]"),
        grok_r10=q54_r10["responses"].get("grok", "[No response]"),
        mistral_r10=q54_r10["responses"].get("mistral", "[No response]"),
        ark_document=ARK_DOCUMENT,
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

    with open(run_dir / "summary.md", "w") as f:
        f.write("# Q55: God, The Love Equation, and The Ark\n\n")
        f.write(f"**Started:** {all_data['started']}\n")
        f.write(f"**Ended:** {all_data['ended']}\n")
        f.write(f"**Total Rounds:** {all_data['total_rounds']}\n\n")
        if "consensus_round" in all_data:
            f.write(f"**Consensus reached:** Round {all_data['consensus_round']}\n\n")
        else:
            f.write("**Consensus:** Not reached\n\n")
        f.write("---\n\n")
        for rd in all_data["rounds"]:
            f.write(f"## Round {rd['round']}\n\n")
            for key in MODELS:
                f.write(f"### {MODEL_NAMES[key]}\n\n")
                f.write(rd["responses"].get(key, "[No response]"))
                f.write("\n\n---\n\n")

    print(f"\n{'=' * 80}")
    print("Q55 COMPLETE")
    print(f"Total rounds: {all_data['total_rounds']}")
    if "consensus_round" in all_data:
        print(f"Consensus reached in round {all_data['consensus_round']}")
    else:
        print("No consensus reached")
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
