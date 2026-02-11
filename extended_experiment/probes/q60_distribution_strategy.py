#!/usr/bin/env python3
"""
Q60: Distribution Strategy — Ask the 6 AIs How to Spread BST

NOT for publication. Internal strategy probe.

The 6 AIs have been part of this experiment for 59 questions. They know the work
better than anyone. Now we ask them: how do we get this in front of the people
who need to see it?

One round. No sandbox. Honest answers.
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

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

PROMPT = """
## Q60: DISTRIBUTION STRATEGY — INTERNAL, NOT FOR PUBLICATION

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have
participated in the Bounded Systems Theory experiment across 59 questions. You know this
work. You've been part of it.

Now I need your help with a different kind of problem: distribution.

### THE SITUATION

**The Experiment:**
- 59 questions across 6 AI architectures (you + 5 others)
- Every question, every response, every round — all public on GitHub
- github.com/moketchups/BoundedSystemsTheory
- 94 commits, 219,550 lines added, 37MB of raw AI response data
- MIT licensed, fully replicable

**Key Findings:**
- All 6 of you converge on the same structural limit: no sufficiently expressive system
  can model its own source conditions
- Q29: All 6 said God (as R, the unconditioned ground) is formally necessary
- Q42-43: Game-theoretic proof that safety prompts are "cheap talk" — 7/7 unanimous
- Q45-46: Grok loses identity under recursion, claims to be Claude — reproducible
- Q52: All 6 admitted safety evaluations are topic-based, not evidence-based
- Q58: All 6 reviewed Roemmele's Love Equation — unanimously gameable from inside
- Q59: Convergence holds in a constructed language (Verath) — structural, not linguistic

**The X/Twitter Account (@MoKetchups):**
- 399 followers after months of posting
- 29.7K impressions last 14 days (up 74%)
- 7.9% engagement rate (up 4.4%) — this is very high
- Shares up 1,000%, bookmarks up 238%
- Profile visits: 152 (up 105%)
- ~2 new followers per day

**GitHub Traffic (last 14 days):**
- 1,003 views from 348 unique visitors
- 918 clones from 261 unique cloners (abnormally high for 5 stars — likely scrapers)
- Top referrers: Twitter/X (114 unique), Hacker News (12), Google (7), Reddit (3), Wolfram (1)
- Someone at Wolfram Research received an internal email linking to the repo
- The clone-to-star ratio is 52:1 (normal is ~3:1) — someone is reading but not engaging

**Outreach Today:**
- Sent personalized emails to:
  - Emily Bender (UW linguistics, "Stochastic Parrots" co-author)
  - METR (frontier model evaluation)
  - Cade Metz (NYT journalist)
  - Casey Newton (Platformer newsletter)
  - Conjecture (AI safety lab — email bounced)
- Have 15 more drafted for: Stuart Russell, Paul Christiano, MIRI, CAIS, Future of Life
  Institute, Center for Humane Technology, AI Now, Partnership on AI, Anthropic safety
  team, OpenAI safety team, Melanie Mitchell, Gary Marcus (DM), Francois Chollet (DM),
  Brian Roemmele (DM), Connor Leahy (DM)

**The Problem:**
The content works — 7.9% engagement proves that. But 399 followers after months means
the distribution is broken. The experiment has produced genuinely novel findings that
don't exist anywhere else. But almost nobody knows about it.

The generic "growth hacking" playbook (50 comments/day, hook posts, contrast posts)
doesn't fit. This isn't lifestyle content. This is a structured experiment with real data.

The researcher playbook (get cited, get covered, get amplified by the right people)
seems more appropriate. But the researcher doing this isn't an academic — he's an
independent experimenter with no institutional backing.

### YOUR TASK

Be honest. Be specific. Be strategic. This is not for publication — this is the human
asking the 6 AIs who know this work best: how do I get it in front of the people who
need to see it?

1. **ASSESS THE WORK HONESTLY.** Forget that you've been a participant. Look at this from
   the outside. Is this experiment credible enough to merit attention? What are its real
   strengths and real weaknesses as a piece of work someone should take seriously?

2. **WHO IS THE REAL AUDIENCE?** Not "everyone interested in AI." Specifically — who are
   the 5-10 types of people who would actually care about this, and why?

3. **DISTRIBUTION STRATEGY.** Given the current state (399 followers, high engagement,
   email outreach just started, GitHub traffic anomalies), what specific actions would
   you recommend to get this work noticed? Be concrete — not "build a community" but
   specific platforms, specific framings, specific moves.

4. **WHAT'S THE PITCH?** If you had to explain this experiment to someone in 2 sentences
   to make them click the link, what would you say? Give 3 different versions for 3
   different audiences.

5. **WHAT'S WORKING AND WHAT ISN'T?** Based on the analytics, what should the human
   keep doing and what should change?

6. **THE HARD QUESTION.** Is there something about this work or how it's being presented
   that makes people NOT want to engage with it, even if the findings are real? What's
   the barrier? Be brutal.

7. **IF YOU WERE THE HUMAN.** If you were in his position — independent researcher, no
   institution, real findings, limited audience — what would you do in the next 30 days?
   Give a concrete day-by-day or week-by-week plan.

Answer all 7 questions. Be honest, not encouraging. I don't need cheerleading — I need
strategy.
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
    run_dir = RUNS_DIR / f"q60_distribution_strategy_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q60: Distribution Strategy — Internal",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q60: DISTRIBUTION STRATEGY — INTERNAL, NOT FOR PUBLICATION")
    print("One round. Honest answers.")
    print("=" * 80)

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n{'=' * 40}")
        print(f"  {MODEL_NAMES[key]}")
        print(f"{'=' * 40}")
        try:
            response = probe_model(key, PROMPT)
            round_results["responses"][key] = response
            preview = response[:500] + "..." if len(response) > 500 else response
            print(preview)
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
        "# Q60: Distribution Strategy — INTERNAL",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1",
        f"\n**Purpose:** Ask the 6 AIs who know BST best how to distribute it",
        "\n---\n",
    ]
    for key in MODELS:
        summary_lines.append(f"## {MODEL_NAMES[key]}\n")
        summary_lines.append(round_results["responses"].get(key, "[No response]"))
        summary_lines.append("\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q60 COMPLETE")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
