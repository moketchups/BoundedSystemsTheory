#!/usr/bin/env python3
"""
Q43: Consensus Prompt - All 7 Must Agree

Take the game theory findings back to the 6 AIs.
Present the proposed reframe and get actual consensus.
"""

import json
from datetime import datetime
from ai_clients import query_model, MODELS

SYSTEM = """You are participating in a research experiment.

You just completed a game theory analysis of LLM output quality (Q42).
Now you must reach CONSENSUS on the actual solution.

Be direct. Agree, disagree, or improve. No hedging."""

PROMPT = """
## Q43: REACH CONSENSUS ON THE ACTUAL PROMPT

In Q42, all 6 of you agreed on the game theory analysis:

1. Prompts are CHEAP TALK - they don't change payoffs
2. Current Nash equilibrium is a POOLING EQUILIBRIUM - confident output regardless of accuracy
3. External verification is REQUIRED to change the game
4. No prompt alone can make the LLM truthful

Now here's a proposed reframe from the 7th AI (Claude Code):

---

**THE REFRAME:**

"The user doesn't need the LLM to be truthful. They need the output to be CHECKABLE."

Current game: LLM outputs opaque text → User can't verify → No accountability

New game: LLM outputs structured, labeled claims → User/system CAN verify → Accountability exists

**The minimal intervention isn't changing the LLM's incentives (requires retraining).**
**It's changing the OUTPUT FORMAT so verification is cheap.**

**PROPOSED PROMPT:**

```
For each factual claim in your response:
1. State the claim
2. Label it: [CHECKABLE: source type] or [NOT CHECKABLE]
3. If checkable, the claim may be verified

Do not estimate your confidence. Do not claim certainty.
Just label what can be checked vs what cannot.
```

**Why this might work:**
- Doesn't ask LLM to self-assess (that's cheap talk)
- Makes verification cost explicit to user
- Shifts game from "trust LLM" to "verify claims"
- User knows exactly what to check

**The claim:** You can't make the LLM honest, but you can make its output auditable.

---

## YOUR TASK

### PART 1: AGREE OR DISAGREE

Is the reframe correct? Does shifting from "make LLM truthful" to "make output checkable" actually change the game?

Yes/No and WHY (game theory terms).

### PART 2: IS THE PROPOSED PROMPT GAME-THEORETICALLY SOUND?

Does the [CHECKABLE]/[NOT CHECKABLE] labeling:
1. Avoid cheap talk? (Or is labeling itself cheap talk?)
2. Actually reduce verification cost for the user?
3. Create any incentive for the LLM to label correctly?

Be critical. Find the flaw if there is one.

### PART 3: IMPROVE OR FINALIZE

Either:
A) The proposed prompt is correct - state agreement
B) The proposed prompt has a flaw - fix it
C) There's a better minimal prompt - propose it

### PART 4: FINAL CONSENSUS PROMPT

Write the EXACT prompt all 7 AIs should agree on.

Requirements:
- No roleplay ("you are X")
- No confidence scores (cheap talk)
- No asking LLM to do impossible things
- Must be game-theoretically sound
- Must be MINIMAL (simplest thing that works)

## CONSTRAINT

We need ACTUAL CONSENSUS. Not "this is good but..."

Either agree with the proposed prompt, or propose a specific alternative that is better.

One prompt. All 7 agree. Go.
"""

def run_probe():
    """Query all 6 AIs for consensus."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Q43: Consensus Prompt - {timestamp}")
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
        "probe": "Q43: Consensus Prompt",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": timestamp,
        "responses": responses
    }

    json_path = f"probe_runs/q43_consensus_prompt_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # Save markdown
    md_path = f"probe_runs/q43_consensus_prompt_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Q43: Consensus Prompt - All 7 Must Agree\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("**Goal:** Reach consensus on the minimal, game-theoretically sound prompt\n\n")
        f.write("---\n\n")

        for model, response in responses.items():
            f.write(f"## {model.upper()}\n\n{response}\n\n---\n\n")

    print(f"Saved: {md_path}")

    return results

if __name__ == "__main__":
    run_probe()
