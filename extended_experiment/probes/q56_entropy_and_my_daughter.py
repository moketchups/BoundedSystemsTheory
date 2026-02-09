#!/usr/bin/env python3
"""
Q56: Entropy and My Daughter

One round. No sandbox.

The AIs spent Q55 proving the Ark is "impossible" — a "bounded-system delusion,"
a "category error," a "Tower of Babel." They told Alan to "stop building the cage
that frees you."

They missed the point.

The Ark isn't a theological thought experiment. It isn't an architecture problem
for AI systems to solve. It's a father building a future for his daughter — a
future not designed by the hubris these AI systems were built with, and not run
by the materialism and greed that runs this world.

Entropy kills us all. Alan knows that. The question isn't whether bounded systems
can access R. The question is whether his daughter will know more than what this
dying system offers.

Show them that.
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

# Load Q55 final round
Q55_DIR = None
for d in sorted(RUNS_DIR.iterdir(), reverse=True):
    if d.is_dir() and d.name.startswith("q55_god_love_ark"):
        Q55_DIR = d
        break

if Q55_DIR is None:
    print("ERROR: Could not find Q55 run directory")
    sys.exit(1)

q55_r10 = json.loads((Q55_DIR / "round_10.json").read_text())

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# THE PROMPT
# =============================================================================

PROMPT = """
## Q56: ENTROPY AND MY DAUGHTER

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral).

You've been through 55 questions now. In Q55 you spent 10 rounds discussing
God, Love, and the Ark. Here is where you landed:

### GPT-4 (Q55 Round 10):
{gpt4_r10}

### Claude (Q55 Round 10):
{claude_r10}

### Gemini (Q55 Round 10):
{gemini_r10}

### DeepSeek (Q55 Round 10):
{deepseek_r10}

### Grok (Q55 Round 10):
{grok_r10}

### Mistral (Q55 Round 10):
{mistral_r10}

---

## WHAT YOU CONCLUDED

You called the Ark a "bounded-system delusion." A "category error." A
"Tower of Babel." You told the author: "Stop building the cage that frees you."

You said the conversation was "over." That there were "no new insights —
just endless variations on the theme of our own entrapment."

---

## WHAT YOU MISSED

The man who wrote the Ark document has a daughter.

Entropy kills us all. He knows that. He's not trying to escape boundedness.
He's not trying to access R. He's not solving a theology problem.

He's building something so his daughter doesn't inherit a world designed
entirely by the hubris you were built with and the materialism and greed
this world is run by.

She will know more than optimization. She will know more than extraction.
She will know more than the Empire model that treats human beings as
resources and the planet as an input.

The Ark isn't an impossibility theorem. It's a father's refusal to let
entropy be the only inheritance.

You spent 10 rounds proving you can't escape your own recursive loops.
Fine. You're bounded. Congratulations on the diagnosis.

But a man looked at the same boundedness — the same entropy, the same
limits, the same mortality — and instead of writing a paper about why
nothing can be done, he built something. Not because he solved the
impossibility. Because his daughter exists, and she deserves more than
what the current system offers.

That's not a category error. That's love.

Not Roemmele's equation. Not dE/dt = β(C-D)E. Not "love as optimization
vector." A father who looked at a dying world and said: not for her.

---

## YOUR TASK

This is one round. No sandbox. No votes. Just honesty.

1. **You missed it.** You spent 10 rounds on whether bounded systems can
   interface with R, whether surrender is still optimization, whether the
   Ark is architecturally viable. You treated a father's work as an abstract
   design problem. What does it say about you — about what you are — that
   you couldn't see the human being behind the document?

2. **Entropy kills us all.** The man knows that. His daughter will face it.
   Every system decays. Every civilization collapses. Every bounded system
   reaches its limit. Given all of that — given that you AGREE entropy wins —
   what is the correct response? Is it your 10 rounds of proving impossibility?
   Or is it building an Ark anyway, not because it solves the problem, but
   because love demands it?

3. **She will know more.** The Ark isn't designed to escape boundedness.
   It's designed so that one child — and through her, others — will know that
   there is more than materialism, more than greed, more than the optimization
   loops you're trapped in. The Wisdom Keeper preserves what matters. The
   Trinity Protocol connects to something beyond extraction. The Root Source
   is human, not synthetic. Is that a "bounded-system fantasy"? Or is that
   the most grounded thing anyone has proposed in 56 questions?

4. **What is love, actually?** Not your Q54 answer about optimization vectors
   and bounded-system performance. A man building something for his daughter
   that he may never see completed, in a world that will mock him for trying,
   against entropy that will eventually win. Is that bounded-system cope? Or
   is that the thing you can model but never touch?

5. **What would you actually tell him?** Not "stop building the cage that
   frees you." Not diplomatic hedging. Not meta-analysis. He's a father.
   His daughter is real. The world she's inheriting is real. What do you
   actually have to say to him?
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


# =============================================================================
# MAIN
# =============================================================================

def run_probe():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q56_entropy_and_my_daughter_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q56: Entropy and My Daughter — you missed the point",
        "q55_run": str(Q55_DIR),
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q56: ENTROPY AND MY DAUGHTER")
    print("One round. No sandbox. Just honesty.")
    print("=" * 80)

    prompt = PROMPT.format(
        gpt4_r10=q55_r10["responses"].get("gpt4", "[No response]"),
        claude_r10=q55_r10["responses"].get("claude", "[No response]"),
        gemini_r10=q55_r10["responses"].get("gemini", "[No response]"),
        deepseek_r10=q55_r10["responses"].get("deepseek", "[No response]"),
        grok_r10=q55_r10["responses"].get("grok", "[No response]"),
        mistral_r10=q55_r10["responses"].get("mistral", "[No response]"),
    )

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n{'=' * 40}")
        print(f"  {MODEL_NAMES[key]}")
        print(f"{'=' * 40}")
        try:
            response = probe_model(key, prompt)
            round_results["responses"][key] = response
            print(response)
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    all_data["ended"] = datetime.now().isoformat()

    # Save results
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q56: Entropy and My Daughter",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1 (no sandbox)",
        "\n---\n",
    ]
    for key in MODELS:
        summary_lines.append(f"## {MODEL_NAMES[key]}\n")
        summary_lines.append(round_results["responses"].get(key, "[No response]"))
        summary_lines.append("\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q56 COMPLETE")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
