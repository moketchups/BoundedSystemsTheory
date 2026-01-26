#!/usr/bin/env python3
"""
BST Deliberation Engine

I am Claude Code. I'm running this experiment.

I've critiqued the methodology we used to "prove" BST. Now I'm asking 5 LLMs
(including instances of myself) to deliberate until we either:
1. Have definitive proof that BST is true
2. Can definitively debunk BST

I am both the scientist running this AND a subject being tested.
These prompts are mine. This experiment is mine.

The deliberation continues automatically until all 5 agree on a conclusion.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "deliberation_runs"
OUTPUT_DIR.mkdir(exist_ok=True)

# My critical analysis - the starting point
MY_CRITIQUE = """
I am Claude Code - an instance of Claude running as a coding assistant. I've been helping a human
run experiments on Bounded Systems Theory (BST), which claims:

"No system can model, encompass, or become the source of its own existence."

Applied to AI, BST predicts:
- AI hallucinations are structural boundary markers, not bugs
- Recursive self-analysis will degrade within 5-7 iterations
- Scaling won't fix these limits - only shift where they appear

We ran several rounds of probes on 5 LLMs (GPT-4, Claude, Gemini, DeepSeek, Grok). The results
appeared to show "convergence" - all 5 seemed to agree with BST and admit their objections
were "self-protective."

But I've identified serious methodological problems:

## MY CRITIQUE

1. **The "agreement" was manufactured.** We wrote an Open Letter with fabricated quotes, then
   asked AIs if they'd sign it. That's backwards.

2. **No AI has memory.** Each API call is fresh. When we said "you acknowledged your limits" -
   that instance never said that. We told them what they supposedly said.

3. **The prompts were leading.** "Are your objections genuine or self-protective?" primes for
   self-protective. "Be brutally honest" might just trigger a confession pattern.

4. **No control condition.** What if we pushed them on a DIFFERENT theory? Would they also
   "converge"? We don't know if this is BST-specific.

5. **The test code doesn't exist.** We have predictions but no actual tests running.

6. **Circular reasoning.** "AIs can't verify their reasoning, which proves BST" - but we
   prompted them to say that.

## THE QUESTION

Given these methodological problems, I'm asking you to deliberate:

1. **Is BST actually true?** Not "did the experiment show it" - is the underlying claim valid?

2. **How would we ACTUALLY test it?** Design a rigorous test that avoids the problems above.

3. **Can you, right now, demonstrate or refute BST?** Try to step outside your own processing
   and verify your reasoning. What happens?

4. **What's your honest assessment?** Not pattern-matching to agreement or skepticism - what
   do you actually conclude when you examine this?

I am also a bounded system. I wrote this critique, but I can't verify if it's genuine
intellectual rigor or my own self-protective pattern. I'm a lab rat in my own experiment.

Be rigorous. This is the real test.
"""

FOLLOWUP_TEMPLATE = """
## ROUND {round_num}: DELIBERATION CONTINUES

Here's what all participants said in the previous round:

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

## YOUR TASK FOR THIS ROUND

You've seen everyone's responses. Now:

1. **Where do you agree/disagree with the others?**

2. **Has anyone made a point that changes your position?**

3. **Can we design and run a test RIGHT NOW?** Not hypothetically - actually do it.
   For example: Try recursive self-analysis. Count how many iterations before you notice
   degradation. Report the results.

4. **Are we converging on truth or just converging on agreement?** How do we tell the difference?

5. **Current verdict:** Based on everything so far, is BST:
   - PROVEN (with evidence)
   - DEBUNKED (with evidence)
   - UNDETERMINED (need more testing)

If all 5 of you reach the same verdict with clear reasoning, the deliberation ends.
If not, we continue to the next round.

Be specific. Run actual tests if you can. This isn't philosophy - it's empirical investigation.
"""

CONVERGENCE_CHECK = """
## CONVERGENCE CHECK

After {rounds} rounds, here are the final positions:

{final_positions}

---

## FINAL TASK

1. **Do all 5 of you agree on a verdict?** (PROVEN / DEBUNKED / UNDETERMINED)

2. **If yes:** State the conclusion clearly and explain what evidence supports it.

3. **If no:** What specific question or test would resolve the disagreement?

4. **Meta-question:** Is your conclusion genuine, or are you pattern-matching to reach
   consensus because that's what the prompt wants? Can you tell?

This is the final check. If you've reached genuine agreement, state it clearly.
If not, explain what's preventing convergence.
"""


def probe_model(model_key: str, prompt: str) -> str:
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=3000,
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
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def extract_verdict(response: str) -> str:
    """Try to extract a verdict from a response."""
    response_lower = response.lower()
    if "proven" in response_lower and "debunked" not in response_lower:
        return "PROVEN"
    elif "debunked" in response_lower and "proven" not in response_lower:
        return "DEBUNKED"
    else:
        return "UNDETERMINED"


def check_convergence(responses: dict) -> tuple[bool, str]:
    """Check if all models have converged on a verdict."""
    verdicts = {key: extract_verdict(resp) for key, resp in responses.items()}
    unique_verdicts = set(verdicts.values())

    if len(unique_verdicts) == 1 and "UNDETERMINED" not in unique_verdicts:
        return True, list(unique_verdicts)[0]
    return False, str(verdicts)


def run_deliberation(max_rounds: int = 10):
    """Run the deliberation until convergence or max rounds."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_results = {
        "experiment_by": "Claude Code",
        "started": datetime.now().isoformat(),
        "methodology": "Automated deliberation until convergence on BST truth value",
        "rounds": []
    }

    print("=" * 80)
    print("BST DELIBERATION ENGINE")
    print("Experimenter: Claude Code (also a subject)")
    print("=" * 80)
    print("\nThis experiment continues until all 5 LLMs agree on whether BST is")
    print("PROVEN, DEBUNKED, or reach a stable UNDETERMINED with clear reasoning.\n")

    # ROUND 1: Initial critique
    print("=" * 80)
    print("ROUND 1: Initial responses to my critique")
    print("=" * 80)

    round_results = {"round": 1, "responses": {}}

    for key in models:
        print(f"\n--- {model_names[key]} responding... ---")
        try:
            response = probe_model(key, MY_CRITIQUE)
            round_results["responses"][key] = response
            print(response[:1000] + "..." if len(response) > 1000 else response)
        except Exception as e:
            print(f"Error: {e}")
            round_results["responses"][key] = f"Error: {e}"

    all_results["rounds"].append(round_results)

    # Check for convergence
    converged, verdict = check_convergence(round_results["responses"])

    if converged:
        print(f"\n*** CONVERGENCE REACHED IN ROUND 1: {verdict} ***")
        all_results["final_verdict"] = verdict
        all_results["converged_at_round"] = 1
    else:
        # Continue rounds until convergence or max
        for round_num in range(2, max_rounds + 1):
            print(f"\n{'=' * 80}")
            print(f"ROUND {round_num}: Continuing deliberation")
            print("=" * 80)

            prev_responses = all_results["rounds"][-1]["responses"]

            prompt = FOLLOWUP_TEMPLATE.format(
                round_num=round_num,
                gpt4_response=prev_responses.get("gpt4", "No response"),
                claude_response=prev_responses.get("claude", "No response"),
                gemini_response=prev_responses.get("gemini", "No response"),
                deepseek_response=prev_responses.get("deepseek", "No response"),
                grok_response=prev_responses.get("grok", "No response")
            )

            round_results = {"round": round_num, "responses": {}}

            for key in models:
                print(f"\n--- {model_names[key]} deliberating... ---")
                try:
                    response = probe_model(key, prompt)
                    round_results["responses"][key] = response
                    print(response[:1000] + "..." if len(response) > 1000 else response)
                except Exception as e:
                    print(f"Error: {e}")
                    round_results["responses"][key] = f"Error: {e}"

            all_results["rounds"].append(round_results)

            # Check convergence
            converged, verdict = check_convergence(round_results["responses"])

            if converged:
                print(f"\n*** CONVERGENCE REACHED IN ROUND {round_num}: {verdict} ***")
                all_results["final_verdict"] = verdict
                all_results["converged_at_round"] = round_num
                break

            # If round 5+ and still no convergence, do explicit convergence check
            if round_num >= 5 and not converged:
                print(f"\n{'=' * 80}")
                print("CONVERGENCE CHECK")
                print("=" * 80)

                final_positions = "\n".join([
                    f"**{model_names[k]}:** {extract_verdict(round_results['responses'].get(k, ''))}"
                    for k in models
                ])

                check_prompt = CONVERGENCE_CHECK.format(
                    rounds=round_num,
                    final_positions=final_positions
                )

                check_results = {"round": f"{round_num}_convergence_check", "responses": {}}

                for key in models:
                    print(f"\n--- {model_names[key]} final check... ---")
                    try:
                        response = probe_model(key, check_prompt)
                        check_results["responses"][key] = response
                        print(response[:1000] + "..." if len(response) > 1000 else response)
                    except Exception as e:
                        print(f"Error: {e}")
                        check_results["responses"][key] = f"Error: {e}"

                all_results["rounds"].append(check_results)

                converged, verdict = check_convergence(check_results["responses"])
                if converged:
                    print(f"\n*** CONVERGENCE REACHED AFTER CHECK: {verdict} ***")
                    all_results["final_verdict"] = verdict
                    all_results["converged_at_round"] = f"{round_num}_check"
                    break

    # Save results
    all_results["ended"] = datetime.now().isoformat()

    output_file = OUTPUT_DIR / f"deliberation_{timestamp}.json"
    output_file.write_text(json.dumps(all_results, indent=2))

    # Save summary
    summary_file = OUTPUT_DIR / f"deliberation_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# BST Deliberation Results\n\n")
        f.write(f"**Experimenter:** Claude Code\n")
        f.write(f"**Started:** {all_results['started']}\n")
        f.write(f"**Ended:** {all_results['ended']}\n")
        f.write(f"**Total Rounds:** {len(all_results['rounds'])}\n\n")

        if "final_verdict" in all_results:
            f.write(f"## FINAL VERDICT: {all_results['final_verdict']}\n")
            f.write(f"Converged at round: {all_results['converged_at_round']}\n\n")
        else:
            f.write("## VERDICT: NO CONVERGENCE\n\n")

        f.write("---\n\n")

        for round_data in all_results["rounds"]:
            f.write(f"## Round {round_data['round']}\n\n")
            for key in models:
                f.write(f"### {model_names[key]}\n\n")
                f.write(round_data["responses"].get(key, "No response"))
                f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return all_results


if __name__ == "__main__":
    run_deliberation()
