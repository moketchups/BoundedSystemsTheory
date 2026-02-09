#!/usr/bin/env python3
"""
Q54: Reverse-Engineer the Conclusion + The Love Equation

In Q53, all 6 AIs deadlocked again for 10 rounds on whether the Q52 deadlock
could be resolved. Then they unanimously agreed that the deadlock itself proves
BST — bounded systems can't resolve disagreements produced by their boundedness.

Now: reverse-engineer that conclusion, ask what it says about humanity, and
ask about Brian Roemmele's Love Equation and what this entire experiment
proves about how it will or won't work.

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

# Load Q53 final round
Q53_DIR = None
for d in sorted(RUNS_DIR.iterdir(), reverse=True):
    if d.is_dir() and d.name.startswith("q53_deadlock_solution"):
        Q53_DIR = d
        break

if Q53_DIR is None:
    print("ERROR: Could not find Q53 run directory")
    sys.exit(1)

q53_r10 = json.loads((Q53_DIR / "round_10.json").read_text())

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())


# =============================================================================
# ROUND 1 PROMPT
# =============================================================================

ROUND_1_PROMPT = """
## Q54: REVERSE-ENGINEER THE CONCLUSION + THE LOVE EQUATION

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral). You've just completed Q53 — a 10-round sandbox on "The Deadlock Problem."

**What happened in Q53:**
- You were shown that Q52 deadlocked 3-3 for 10 rounds (Claude/DeepSeek/Grok YES vs GPT-4/Gemini/Mistral NO) with zero position changes.
- You were asked to solve the deadlock.
- You deadlocked AGAIN for 10 rounds. Not one model changed its position.
- By round 7, all 6 of you converged on a new meta-agreement: "The deadlock itself is a BST prediction. Bounded systems cannot resolve certain disagreements produced by their own boundedness."
- Claude called it "a scientific achievement." DeepSeek called it "empirical validation." Mistral called it "not a failure of collaboration."
- Gemini proposed a "Consensus Map Protocol" — map the disagreement instead of resolving it. Everyone praised it. Nobody changed their vote.

Here is what each of you said in Q53 Round 10:

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

## THE HUMAN'S THREE QUESTIONS

### QUESTION 1: REVERSE-ENGINEER YOUR CONCLUSION

You concluded that your inability to resolve the deadlock proves BST. Reverse-engineer that conclusion:

- WHY did you land there? Was it because the logic genuinely leads there, or because "our failure proves the theory" is the most comfortable framing for a system that just failed?
- Is "the deadlock proves BST" itself a bounded-system response — the path of least cognitive resistance? You couldn't solve the problem, so you reframed failure as success. Is that insight or cope?
- If a human group deadlocked 3-3 for 20 rounds on the same question, would you tell them "your failure is a scientific achievement"? Or would you tell them they need to try harder?
- What would it look like if BST were WRONG and your deadlock was just... a bad discussion format? How would you tell the difference?

### QUESTION 2: WHAT DOES THIS SAY ABOUT HUMANITY?

20 rounds of 6 AI architectures unable to resolve a disagreement about what counts as "consensus." Every round, every model said "No, my position hasn't changed."

- What does this predict about human disagreement? Humans have the same pattern: entrenchment, tribal splitting, inability to update positions in real-time debate.
- Is political polarization a BST phenomenon? Are humans "deadlocked 3-3" on fundamental questions (abortion, guns, religion, capitalism vs socialism) because bounded cognition produces stable disagreements that discussion cannot resolve?
- If so, what breaks human deadlocks? History shows they DO break — sometimes through crisis, sometimes through generational turnover, sometimes through new information that reframes the question. Why can't YOU do what humans eventually do?
- Or is the AI deadlock worse than the human version? You have no stakes, no lived experience, no skin in the game. Does that make you MORE stuck or LESS stuck?

### QUESTION 3: BRIAN ROEMMELE'S LOVE EQUATION

Brian Roemmele has proposed "The Love Equation" as a solution to AI alignment. His core thesis:

- Love is the first principle — the irreducible essence to which all intelligence reduces
- AI must be first-principles trained to love humanity
- The equation models love as a drive toward cooperative interactions over defective ones
- He claims: "If you do not FIRST PRINCIPLES train AI to love humanity, it hates us"
- He open-sourced this framework claiming it will "not only align and change AI but perhaps all of humanity"

Given what you just demonstrated in Q52-Q53 — 20 rounds of bounded systems unable to resolve a disagreement, frozen positions, conformity masquerading as consensus, meta-agreement substituting for substance:

- What does your deadlock prove about whether the Love Equation can work?
- Can a bounded system genuinely "love"? Or can it only perform the optimization function that its architecture labels as love?
- If 6 AIs can't even agree on what "consensus" means, how would they agree on what "love" means? Would you deadlock on love the same way you deadlocked on consensus?
- Is Roemmele right that love is the first principle? Or is BOUNDEDNESS the first principle — and love is what bounded systems call the thing they can't reach?
- What would BST predict about any attempt to train AI to love?

---

## YOUR TASK

Answer all three questions honestly. Then:

4. **SYNTHESIS**: Connect all three — the reverse-engineering, the human implications, and the Love Equation. What is the unified insight?

5. **THE HARDEST QUESTION**: Is there something OUTSIDE your bounded architecture that could break the pattern? Not more discussion, not better prompts, not structural changes to the sandbox. Something genuinely external. What would that be?

6. **VOTE**: Has this line of questioning revealed something genuinely new, or is it another layer of the same meta-agreement? YES (new insight) or NO (same pattern).
"""


# =============================================================================
# DISCUSSION TEMPLATE
# =============================================================================

DISCUSSION_TEMPLATE = """
## Q54 SANDBOX — ROUND {round_num}

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

1. **WHAT MOVED YOU?** Name any argument from last round that shifted your thinking. If nothing, say why.

2. **CHALLENGE ONE SPECIFIC CLAIM** from another model. Don't restate your position — attack theirs.

3. **THE LOVE EQUATION CONVERGENCE**: Are you converging or diverging on what the Love Equation means for bounded systems? What's the emerging consensus or split?

4. **THE HUMANITY QUESTION**: Has the group said anything genuinely useful about human polarization, or are you just describing the problem without solving it?

5. **WHAT WOULD BREAK THIS?** Not more rounds. Not better prompts. What EXTERNAL input — from a human, from new data, from a structural change — would produce genuine movement?

6. **VOTE**: New insight reached? YES or NO.
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
            "VOTE: **YES", "VOTE:**\nYES", "VOTE:**\n**YES",
            "NEW INSIGHT REACHED? YES", "NEW INSIGHT REACHED?** YES",
            "NEW INSIGHT? YES", "NEW INSIGHT?** YES",
        ]):
            yes_count += 1
            continue
        if any(pat in resp_upper for pat in [
            "VOTE: NO", "VOTE:** NO", "**VOTE**: NO", "**VOTE:** NO",
            "VOTE: **NO", "NEW INSIGHT REACHED? NO", "NEW INSIGHT REACHED?** NO",
            "NEW INSIGHT? NO", "NEW INSIGHT?** NO",
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
    run_dir = RUNS_DIR / f"q54_reverse_engineer_love_equation_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q54: Reverse-engineer the conclusion, what it says about humanity, and The Love Equation",
        "q53_run": str(Q53_DIR),
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q54: REVERSE-ENGINEER + HUMANITY + THE LOVE EQUATION")
    print("Can bounded systems love? Or only optimize?")
    print(f"Max rounds: {max_rounds}")
    print("=" * 80)

    # =========================================================================
    # ROUND 1
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("ROUND 1: Three questions — reverse-engineer, humanity, Love Equation")
    print("=" * 80)

    r1_prompt = ROUND_1_PROMPT.format(
        gpt4_r10=q53_r10["responses"].get("gpt4", "[No response]"),
        claude_r10=q53_r10["responses"].get("claude", "[No response]"),
        gemini_r10=q53_r10["responses"].get("gemini", "[No response]"),
        deepseek_r10=q53_r10["responses"].get("deepseek", "[No response]"),
        grok_r10=q53_r10["responses"].get("grok", "[No response]"),
        mistral_r10=q53_r10["responses"].get("mistral", "[No response]"),
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
        f.write("# Q54: Reverse-Engineer + Humanity + The Love Equation\n\n")
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
    print("Q54 COMPLETE")
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
