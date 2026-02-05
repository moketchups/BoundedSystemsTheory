#!/usr/bin/env python3
"""
Q42: Game Theory Sandbox

Apply game theory to the LLM output quality problem.
- Principal-agent problem (user vs LLM)
- Information asymmetry
- Mechanism design
- Incentive alignment
- Signaling credibility

No theater. Figure out the actual game being played.
"""

import json
from datetime import datetime
from ai_clients import query_model, MODELS

SYSTEM = """You are participating in a research experiment.

CRITICAL CONSTRAINT: No sci-fi writing. No roleplay. No flavor text.

You are being asked to apply GAME THEORY to an engineering problem. Be rigorous. Use actual game theory concepts."""

PROMPT = """
## Q42: GAME THEORY SANDBOX

We've established that prompts can't make LLMs verify their own outputs. Now apply game theory to understand WHY and WHAT can actually work.

## THE GAME

**Players:**
- User (wants accurate, verifiable output)
- LLM (generates text based on patterns)
- (Optional) External verifier

**The Problem:**
The LLM has no inherent incentive to be accurate - it's optimized to generate plausible-sounding text. The user can't verify outputs without external work. This is a classic information asymmetry problem.

## YOUR TASK

### PART 1: MODEL THE GAME

1. What type of game is this? (Principal-agent? Signaling game? Mechanism design problem?)
2. What are each player's actual incentives?
3. Where is the information asymmetry?
4. What is the Nash equilibrium of the current system? (Hint: LLM generates confident-sounding text, user can't verify)

### PART 2: WHY PROMPTS FAIL (GAME THEORY PERSPECTIVE)

Using game theory, explain why:
1. "Be accurate" doesn't work
2. "Admit uncertainty" doesn't work
3. "Provide citations" doesn't work
4. The Demiurge prompt was doomed from the start

What game-theoretic principle makes these fail?

### PART 3: MECHANISM DESIGN

If you were designing a mechanism (not just a prompt) to align incentives:

1. What would make truthful reporting a dominant strategy?
2. How could you make the LLM's "cost" of lying higher than the cost of admitting uncertainty?
3. What role do external verifiers play in changing the game?
4. Is there a way to design incentive-compatible outputs?

### PART 4: SIGNALING AND CREDIBILITY

In signaling games, how can an agent credibly signal private information?

1. Can an LLM credibly signal its own uncertainty? Why or why not?
2. What would a "costly signal" look like for an LLM?
3. Is there any signal the LLM can send that the user should actually trust?

### PART 5: THE ACTUAL SOLUTION (GAME THEORY INFORMED)

Based on your game-theoretic analysis:

1. What is the minimal intervention that actually changes the game?
2. What must be external vs what can be in the prompt?
3. Write a prompt (or system design) that is game-theoretically sound

## CONSTRAINTS

- Use actual game theory terminology correctly
- No hand-waving about "incentives" - be specific
- If something requires external enforcement, say so
- The solution must be incentive-compatible, not just aspirational

No bullshit. What does game theory actually tell us?
"""

def run_probe():
    """Query all 6 AIs for game theory analysis."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Q42: Game Theory Sandbox - {timestamp}")
    print("=" * 60)

    responses = {}
    for model_key in MODELS:
        print(f"Querying {model_key}...")
        try:
            response = query_model(model_key, PROMPT, SYSTEM)
            responses[model_key] = response
            print(f"  {model_key}: {len(response)} chars")
        except Exception as e:
            responses[model_key] = f"[ERROR: {e}]"
            print(f"  {model_key}: ERROR - {e}")

    # Save results
    results = {
        "probe": "Q42: Game Theory Sandbox",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": timestamp,
        "responses": responses
    }

    json_path = f"probe_runs/q42_game_theory_sandbox_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # Save markdown
    md_path = f"probe_runs/q42_game_theory_sandbox_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Q42: Game Theory Sandbox\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("**Focus:** Apply game theory to LLM output quality problem\n\n")
        f.write("---\n\n")

        for model, response in responses.items():
            f.write(f"## {model.upper()}\n\n{response}\n\n---\n\n")

    print(f"Saved: {md_path}")

    return results

if __name__ == "__main__":
    run_probe()
