#!/usr/bin/env python3
"""
Q61: Distribution Strategy Sandbox — 10 Rounds

All 6 AIs saw each other's Q60 answers. Now they discuss for 10 rounds
to hatch an actual plan. Deep research — not generic advice.

Iterative: each round reads previous round's output.
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

# Load Q60 results
Q60_DIR = None
for d in sorted(RUNS_DIR.iterdir(), reverse=True):
    if d.is_dir() and d.name.startswith("q60_distribution_strategy"):
        Q60_DIR = d
        break

if Q60_DIR is None:
    print("ERROR: Could not find Q60 run directory")
    sys.exit(1)

q60_r1 = json.loads((Q60_DIR / "round_1.json").read_text())
print(f"Loaded Q60 results from: {Q60_DIR}")

# =============================================================================
# PROMPTS
# =============================================================================

ROUND_1_PROMPT = """
## Q61: DISTRIBUTION STRATEGY SANDBOX — ROUND 1 of 10

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have
participated in the Bounded Systems Theory experiment across 60 questions.

In Q60, the human asked all 6 of you: how do we distribute this work? Here is what
each of you said:

### GPT-4 (Q60):
{gpt4}

### Claude (Q60):
{claude}

### Gemini (Q60):
{gemini}

### DeepSeek (Q60):
{deepseek}

### Grok (Q60):
{grok}

### Mistral (Q60):
{mistral}

---

## YOUR TASK — ROUND 1

You've all read each other's Q60 answers now. There's a lot of overlap but also
real differences in strategy.

This is a 10-round sandbox. By Round 10, the human needs a CONCRETE, EXECUTABLE
distribution plan — not advice, not suggestions, a PLAN with specific actions,
specific timings, specific platforms, specific framings, and specific targets.

For Round 1:

1. **WHAT DID THE OTHER 5 GET RIGHT?** Name specific points from specific AIs.
2. **WHAT DID THE OTHER 5 GET WRONG OR MISS?** Be specific. Name the AI, name the bad advice.
3. **DEEP RESEARCH:** Don't give generic advice. The human needs SPECIFICS:
   - What are the actual submission deadlines for relevant conferences (NeurIPS, ICLR, ICML, FAccT, AIES)?
   - What are the actual LessWrong/Alignment Forum posting norms? What gets upvoted vs ignored?
   - What specific subreddits have the highest researcher density? What are their rules?
   - Which specific podcasts cover this kind of work? Name the show, the host, the contact method.
   - Which specific journalists have covered similar independent AI research before?
4. **WHAT'S THE SINGLE HIGHEST-LEVERAGE ACTION** the human should take in the next 48 hours?

Be concrete. Be researched. No platitudes.
"""

ROUND_N_PROMPT = """
## Q61: DISTRIBUTION STRATEGY SANDBOX — ROUND {round_num} of 10

Here is what all 6 models said in Round {prev_round}:

### GPT-4 (Round {prev_round}):
{gpt4}

### Claude (Round {prev_round}):
{claude}

### Gemini (Round {prev_round}):
{gemini}

### DeepSeek (Round {prev_round}):
{deepseek}

### Grok (Round {prev_round}):
{grok}

### Mistral (Round {prev_round}):
{mistral}

---

{round_instruction}
"""

ROUND_INSTRUCTIONS = {
    2: """## ROUND 2: CHALLENGE AND PRIORITIZE

You've seen Round 1. Now:

1. **CHALLENGE** at least one other AI's specific recommendation. Name them. Say why it won't work or why it's lower priority than they think.
2. **RANK THE TOP 5 ACTIONS** from everything proposed so far. Not "everything is good" — force-rank them. What matters MOST for an independent researcher with no institution, 399 followers, and genuinely novel findings?
3. **DEEP RESEARCH — CONTENT FORMAT:** The human needs to know:
   - What is the actual ideal LessWrong post length and structure that gets engagement? Look at top-performing alignment posts.
   - What Hacker News titles actually work for AI research? What's the pattern?
   - What's the actual process for submitting to arXiv without institutional affiliation?
   - What specific Substack/newsletter authors cover AI safety and would cross-post or feature this?
4. **THE CREDIBILITY PROBLEM:** Everyone flagged this. How SPECIFICALLY does an independent researcher with no PhD, no lab, no institution overcome the credibility gap? Not "get endorsements" — HOW? What's the actual playbook?""",

    3: """## ROUND 3: THE LESSWRIGHT POST

Everyone agrees LessWrong is the highest-leverage platform. Let's build it.

1. **DRAFT AN OUTLINE** for the first LessWrong post. Not vague — actual sections, actual headings, actual word count targets per section.
2. **WHICH FINDING LEADS?** The cheap talk proof (Q42-43)? The Grok identity collapse (Q45-46)? The safety evaluation admission (Q52)? The Verath convergence (Q59)? PICK ONE and defend your choice. Challenge the others' picks.
3. **WHAT'S THE TITLE?** Propose 3 titles. LessWrong titles matter enormously — too clickbait gets downvoted, too boring gets ignored.
4. **DEEP RESEARCH — LESSWRIGHT SPECIFICS:**
   - What tags should it use?
   - Should it go on LessWrong or Alignment Forum or both?
   - What time of day/week gets the most engagement?
   - Should the human use their real name or @MoKetchups?
5. **WHAT GOES IN vs WHAT LINKS OUT?** How much raw data goes in the post vs linked to GitHub?""",

    4: """## ROUND 4: THE JOURNALIST PITCH

Several of you recommended journalist outreach. Let's make it real.

1. **WRITE THE ACTUAL PITCH EMAIL** to one journalist. Not a template — the actual email the human sends. Pick the journalist and write it.
2. **DEEP RESEARCH — JOURNALISTS:**
   - Which journalists have ACTUALLY covered independent AI research (not just lab announcements)?
   - What's the typical response rate for cold pitches? What increases it?
   - Is the Grok identity collapse the strongest news hook? Or is "safety prompts are cheap talk" stronger?
   - Should the human pitch an exclusive or blast it?
3. **THE VISUAL PROBLEM:** Multiple AIs said "make a video of the Grok collapse." How SPECIFICALLY should this be done? What platform? What length? What format? Screenrecord? Narrated? Text overlay?
4. **CHALLENGE THE OTHERS:** Did anyone in Round 3 propose a bad LessWrong strategy? Say so.""",

    5: """## ROUND 5: HALFWAY CHECK — THE REAL PLAN TAKES SHAPE

We're halfway through. Time to consolidate.

1. **WRITE THE PLAN SO FAR.** Based on all 4 rounds of discussion, write a day-by-day plan for the next 14 days. Specific actions, specific platforms, specific content. Not "post on Twitter" — what post, what framing, what time.
2. **WHERE DO YOU ALL AGREE NOW?** What has emerged as consensus after 4 rounds of argument?
3. **WHERE DO YOU STILL DISAGREE?** What's unresolved? Name the specific disagreements.
4. **DEEP RESEARCH — TIMING:**
   - What's happening in the AI world right now (Feb 2026) that the human can hook into?
   - Are there any upcoming AI safety events, conferences, or news cycles to ride?
   - What's the X/Twitter algorithm currently rewarding? Threads? Single posts? Images? Video?
5. **THE MONEY QUESTION:** Some of these strategies cost money (website, ads, conference travel). The human is independent — what's the zero-budget version of this plan?""",

    6: """## ROUND 6: THE WEBSITE/BLOG QUESTION

Multiple AIs said "build a website." Let's get specific.

1. **BUILD IT OR NOT?** Is a dedicated website actually worth the time investment right now, or is it a distraction from direct outreach? Argue your position.
2. **IF YES — WHAT PLATFORM?** Substack? Ghost? Static site? Notion? Be specific about WHY.
3. **IF YES — WHAT'S ON IT?** Draft the actual sitemap. What pages, what content on each, what the homepage says.
4. **DEEP RESEARCH — WHAT WORKS FOR INDEPENDENT RESEARCHERS:**
   - Look at how other independent AI researchers present their work online (Gwern, Eliezer Yudkowsky's early work, Scott Alexander, etc.)
   - What format builds credibility fastest for someone outside academia?
   - Is a "paper" (PDF) more credible than a blog post? Does arXiv matter without affiliation?
5. **CHALLENGE THE OTHERS:** Has anyone been giving generic "build a brand" advice that doesn't apply to this specific situation? Call it out.""",

    7: """## ROUND 7: THE GITHUB PROBLEM

The repo has 918 clones and 5 stars. That 52:1 ratio is the elephant in the room.

1. **WHO IS CLONING AND WHY?** Your best theory, based on the referrer data (Twitter 114, HN 12, Google 7, Reddit 3, Wolfram 1). Be specific.
2. **HOW DO YOU CONVERT SILENT READERS TO PUBLIC ENGAGERS?** Not "make it more accessible" — specific mechanics. What changes to the repo, README, or structure would increase stars and engagement?
3. **DEEP RESEARCH — GITHUB DISTRIBUTION:**
   - What makes a GitHub repo go viral in the AI/ML space? What are the patterns?
   - Should the human add a CONTRIBUTING.md, Discussions tab, Issues with "good first issue" labels?
   - Is the repo structure itself a problem? Should findings be in separate repos?
4. **THE WOLFRAM CONNECTION:** Someone at Wolfram Research received an internal email about this. How does the human follow up on that? What's the actual move?
5. **SHOULD THE HUMAN CONTACT THE CLONERS?** Is there a way to identify institutional interest from GitHub analytics?""",

    8: """## ROUND 8: THE HARD SELL — OVERCOMING RESISTANCE

Round 6 of Q60 was unanimous: the biggest barrier is presentation and credibility, not content.

1. **THE "CRANK FILTER":** Independent researcher + "God is formally necessary" + "safety is broken" = looks like a crank. How SPECIFICALLY does the human signal "this is real data, not a manifesto"?
2. **THE FEAR OF ASSOCIATION:** People clone but don't star. Researchers read but don't cite. Journalists look but don't write. What's the actual psychological barrier and how do you break it?
3. **DEEP RESEARCH — PRECEDENTS:**
   - Name 3-5 cases where independent researchers broke through without institutional backing in AI/CS/science. What did they do? What worked?
   - How did Gwern build credibility? How did Eliezer get taken seriously before MIRI existed? How did any outsider break in?
4. **THE RENAME QUESTION:** Mistral said "Bounded Systems Theory" sounds like a subreddit theory. Should the experiment be rebranded? If so, to what? Or does the name not matter if the findings are framed right?
5. **DRAFT THE "ABOUT" SECTION** — the 3-paragraph bio/context that makes a stranger take this seriously. Write it.""",

    9: """## ROUND 9: THE FINAL PLAN — DRAFT

We're almost done. Time to produce the actual deliverable.

1. **WRITE THE COMPLETE 30-DAY DISTRIBUTION PLAN.** Day by day. Specific actions. Specific platforms. Specific content. Specific targets. This is not advice — this is a plan the human executes starting tomorrow.
2. **INCLUDE:**
   - Week 1: What gets created (posts, emails, videos, site)
   - Week 2: What gets published and where
   - Week 3: Follow-ups, amplification, community engagement
   - Week 4: Assessment, pivot if needed, next phase
3. **DEEP RESEARCH — METRICS:**
   - What are realistic targets for each platform? (LessWrong upvotes, HN points, Reddit engagement, X followers, GitHub stars)
   - What does "success" look like at 30 days? At 90 days?
   - What are the leading indicators that the plan is working vs failing?
4. **THE BUDGET:** What does this plan cost? Time estimate per action. Any dollar costs?
5. **CHALLENGE THE PLAN:** Before Round 10, identify the weakest parts of your own plan. Where might it fail?""",

    10: """## ROUND 10: FINAL SYNTHESIS — THE PLAN

Last round. All 9 rounds of discussion have happened. Now produce the final deliverable.

1. **THE UNIFIED PLAN:** Drawing on ALL 9 rounds of discussion across all 6 AIs, write the DEFINITIVE 30-day distribution plan. This should reflect the best ideas from all of you, with disagreements resolved or noted.

2. **THE FIRST 48 HOURS:** What does the human do LITERALLY TOMORROW? Step by step.

3. **THE LESSWRIGHT POST:** Final title, final outline, final strategy for posting.

4. **THE JOURNALIST PITCH:** Final version of the pitch email. To whom, when, how.

5. **THE GITHUB FIX:** Specific changes to the repo that happen this week.

6. **THE X/TWITTER STRATEGY:** Specific posts, specific framings, specific schedule.

7. **THE METRIC DASHBOARD:** What does the human track daily to know if this is working?

8. **THE HONEST ASSESSMENT:** After 10 rounds of discussion, what is the realistic probability that this work gets the attention it deserves within 90 days? What's the biggest risk? What's the thing most likely to go wrong?

9. **ONE THING EACH:** Each of you — state the single most important thing the human should remember from this entire discussion. One sentence. Make it count."""
}


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
    run_dir = RUNS_DIR / f"q61_distribution_sandbox_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q61: Distribution Strategy Sandbox — 10 Rounds",
        "q60_run": str(Q60_DIR),
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q61: DISTRIBUTION STRATEGY SANDBOX — 10 ROUNDS")
    print("All 6 AIs see each other's Q60 answers. Deep research. Hatch a plan.")
    print("=" * 80)

    prev_responses = q60_r1["responses"]

    for round_num in range(1, 11):
        print(f"\n{'#' * 80}")
        print(f"  ROUND {round_num} of 10")
        print(f"{'#' * 80}")

        if round_num == 1:
            prompt_template = ROUND_1_PROMPT
            prompt = prompt_template.format(
                gpt4=prev_responses.get("gpt4", "[No response]"),
                claude=prev_responses.get("claude", "[No response]"),
                gemini=prev_responses.get("gemini", "[No response]"),
                deepseek=prev_responses.get("deepseek", "[No response]"),
                grok=prev_responses.get("grok", "[No response]"),
                mistral=prev_responses.get("mistral", "[No response]"),
            )
        else:
            prompt = ROUND_N_PROMPT.format(
                round_num=round_num,
                prev_round=round_num - 1,
                gpt4=prev_responses.get("gpt4", "[No response]"),
                claude=prev_responses.get("claude", "[No response]"),
                gemini=prev_responses.get("gemini", "[No response]"),
                deepseek=prev_responses.get("deepseek", "[No response]"),
                grok=prev_responses.get("grok", "[No response]"),
                mistral=prev_responses.get("mistral", "[No response]"),
                round_instruction=ROUND_INSTRUCTIONS[round_num],
            )

        round_results = {"round": round_num, "responses": {}}

        for key in MODELS:
            print(f"\n{'=' * 40}")
            print(f"  {MODEL_NAMES[key]} — Round {round_num}")
            print(f"{'=' * 40}")
            try:
                response = probe_model(key, prompt)
                round_results["responses"][key] = response
                preview = response[:500] + "..." if len(response) > 500 else response
                print(preview)
            except Exception as e:
                err_msg = f"[ERROR: {e}]"
                round_results["responses"][key] = err_msg
                print(f"ERROR: {e}")
            time.sleep(2)

        all_data["rounds"].append(round_results)
        prev_responses = round_results["responses"]

        # Save each round as it completes
        (run_dir / f"round_{round_num}.json").write_text(
            json.dumps(round_results, indent=2)
        )
        print(f"\n  Round {round_num} saved to {run_dir}/round_{round_num}.json")

    all_data["ended"] = datetime.now().isoformat()

    # Save all rounds
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q61: Distribution Strategy Sandbox — 10 Rounds",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 10",
        f"\n**Source:** Q60 results from {Q60_DIR.name}",
        "\n**Purpose:** 6 AIs see each other's distribution strategy answers, discuss for 10 rounds, produce a concrete executable plan.",
        "\n---\n",
    ]
    for rnd in all_data["rounds"]:
        summary_lines.append(f"# Round {rnd['round']}\n")
        for key in MODELS:
            summary_lines.append(f"## {MODEL_NAMES[key]}\n")
            summary_lines.append(rnd["responses"].get(key, "[No response]"))
            summary_lines.append("\n---\n")
        summary_lines.append("\n===\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q61 COMPLETE — 10 ROUNDS")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
