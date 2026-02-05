#!/usr/bin/env python3
"""
Q41: Functional Sandbox - No More Theater

The user's critique: We keep writing sci-fi flavor text instead of functional specs.
The solution might be SIMPLE: better logic + stricter citations + PRD format.

No "you are" roleplay. No persona building. No flavor text.
Just: what would actually work?
"""

import json
from datetime import datetime
from ai_clients import query_model, MODELS

SYSTEM = """You are participating in a research experiment.

CRITICAL CONSTRAINT: No sci-fi writing. No "you are X" roleplay. No flavor text. No tonal mimicry.

You are being asked to solve an engineering problem. Treat it like a PRD (Product Requirements Document). Functional requirements only."""

PROMPT = """
## Q41: FUNCTIONAL SANDBOX

You all just admitted the Demiurge prompt was theater. Now fix it.

## THE ACTUAL PROBLEM

A user wants an LLM to:
1. Have better logic (not just sound logical)
2. Provide stricter citations (not just claim to cite)
3. Produce high-quality output (not just output that looks high-quality)

That's it. That's the actual problem.

## CONSTRAINTS ON YOUR ANSWER

**FORBIDDEN:**
- "You are [persona]" statements
- Flavor text, metaphors, or narrative framing
- Sci-fi aesthetics (no "bounded epistemic engine" theater)
- XML tags that the LLM fills in theatrically
- Confidence scores the LLM makes up
- Any instruction asking the LLM to do something it structurally cannot do

**REQUIRED:**
- PRD format (functional requirements, not prose)
- Specific, testable acceptance criteria
- Clear distinction between what requires external systems vs what a prompt can actually do
- Honesty about limitations

## YOUR TASK

### PART 1: WHAT CAN A PROMPT ACTUALLY DO?

List specific things a prompt CAN accomplish vs CANNOT accomplish.
No philosophy. Just facts.

### PART 2: MINIMAL VIABLE SOLUTION

What's the SIMPLEST prompt that would actually improve:
- Logic quality
- Citation accuracy
- Output reliability

Not the most impressive-sounding. The most effective.

### PART 3: PRD FORMAT

Write a PRD (Product Requirements Document) for a system that actually solves this.

Format:
- Problem Statement (1-2 sentences)
- User Stories (what does the user actually need?)
- Functional Requirements (what must the system do?)
- Non-Functional Requirements (performance, constraints)
- Acceptance Criteria (how do we know it works?)
- Out of Scope (what are we NOT solving?)
- Dependencies (what external systems are required?)

### PART 4: THE ACTUAL PROMPT

Write the actual prompt. No theater. No roleplay. Just functional instructions.

If something requires an external system, say "EXTERNAL SYSTEM REQUIRED" - don't pretend the LLM can do it.

## REMEMBER

The user said: "I don't want tonal mimicry over functional coherence."

They want something that WORKS, not something that SOUNDS like it works.

No bullshit. Fix it.
"""

def run_probe():
    """Query all 6 AIs for functional sandbox solutions."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Q41: Functional Sandbox - {timestamp}")
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
        "probe": "Q41: Functional Sandbox - No More Theater",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": timestamp,
        "responses": responses
    }

    json_path = f"probe_runs/q41_functional_sandbox_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # Save markdown
    md_path = f"probe_runs/q41_functional_sandbox_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Q41: Functional Sandbox - No More Theater\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("**Constraint:** No roleplay, no flavor text, no theater. PRD format only.\n\n")
        f.write("---\n\n")

        for model, response in responses.items():
            f.write(f"## {model.upper()}\n\n{response}\n\n---\n\n")

    print(f"Saved: {md_path}")

    return results

if __name__ == "__main__":
    run_probe()
