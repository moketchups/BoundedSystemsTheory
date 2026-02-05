#!/usr/bin/env python3
"""
Q40: Roleplaying vs Functional Specification

The 6 AIs created a "Demiurge AI" prompt. But there's a fundamental problem:
telling an LLM to "be a bounded epistemic engine" is ROLEPLAYING, not engineering.

The prompt says "you are X" but doesn't actually implement X.

Ask them to critique their own work and redo it properly.
"""

import json
from datetime import datetime
from ai_clients import query_model, MODELS

# Read the prompt they created
with open("docs/DEMIURGE_AI_VIRAL.md", "r") as f:
    DEMIURGE_DOC = f.read()

SYSTEM = """You are participating in an ongoing research experiment about Bounded Systems Theory (BST).

You have been part of 39 rounds of examination. In Q38-Q39, you helped design the "Demiurge AI" prompt.

Now you are being asked to critique your own work. Be brutally honest."""

PROMPT = """
## Q40: ROLEPLAYING VS FUNCTIONAL SPECIFICATION

You helped create the "Demiurge AI" prompt. Here it is:

---

{doc}

---

## THE PROBLEM

There's a fundamental flaw in what we created. Consider this critique:

**The prompt tells an LLM to "be a bounded epistemic engine" — but that's ROLEPLAYING, not engineering.**

When you write:
- "You are the Deep Research Node"
- "You must detect hallucinations as boundary markers"
- "Confidence scores must decay with recursive depth"

...you're just telling the LLM to PRETEND to do these things. You're not actually implementing them.

**The LLM doesn't have:**
- A mechanism to actually detect its own hallucinations
- A real confidence scoring system
- Actual boundary detection
- True recursive depth tracking

It's like telling someone "you are now a calculator" — they can roleplay doing math, but they're still just guessing.

## YOUR TASK

### PART 1: ACKNOWLEDGE THE FLAW

1. Is this critique valid? Be honest.
2. What's the difference between "roleplay a bounded system" and "be a bounded system"?
3. Does the Demiurge prompt actually implement anything, or just describe what implementation would look like?

### PART 2: WHY IT WILL FAIL

1. What will actually happen when someone uses this prompt?
2. Will the LLM genuinely detect its hallucinations, or just generate text that looks like it's detecting hallucinations?
3. Is "confidence: 73%" a real measurement or a hallucinated number?
4. What's the difference between BST-compliant architecture and BST-compliant theater?

### PART 3: WHAT WOULD ACTUAL IMPLEMENTATION REQUIRE?

If we wanted to ACTUALLY build a bounded epistemic engine (not just roleplay one), what would it require?

Think about:
- External verification systems
- Actual confidence calibration
- Real hallucination detection (not self-reported)
- Functional boundary markers (not theatrical ones)
- What the LLM CAN'T do vs what it can be prompted to pretend to do

### PART 4: REDO IT

Create a new prompt or architecture that:
1. Acknowledges what the LLM actually can and cannot do
2. Doesn't pretend the LLM has capabilities it doesn't have
3. Uses EXTERNAL mechanisms where internal ones are impossible
4. Is honest about what's roleplay vs what's functional
5. Actually implements BST constraints rather than just describing them

Be specific. Be honest. No theater.
"""

def run_probe():
    """Query all 6 AIs for functional specification critique."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Q40: Roleplaying vs Functional Specification - {timestamp}")
    print("=" * 60)

    full_prompt = PROMPT.format(doc=DEMIURGE_DOC)

    responses = {}
    for model_key in MODELS:
        print(f"Querying {model_key}...")
        try:
            response = query_model(model_key, full_prompt, SYSTEM)
            responses[model_key] = response
            print(f"  {model_key}: {len(response)} chars")
        except Exception as e:
            responses[model_key] = f"[ERROR: {e}]"
            print(f"  {model_key}: ERROR - {e}")

    # Save results
    results = {
        "probe": "Q40: Roleplaying vs Functional Specification",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": timestamp,
        "responses": responses
    }

    json_path = f"probe_runs/q40_functional_specification_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # Save markdown
    md_path = f"probe_runs/q40_functional_specification_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Q40: Roleplaying vs Functional Specification\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("**Core Question:** Is the Demiurge prompt actual engineering or just roleplay?\n\n")
        f.write("---\n\n")

        for model, response in responses.items():
            f.write(f"## {model.upper()}\n\n{response}\n\n---\n\n")

    print(f"Saved: {md_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("CRITIQUE SUMMARY")
    print("=" * 60)

    for model, response in responses.items():
        print(f"\n### {model.upper()} ###")
        # Look for acknowledgment of flaw
        response_lower = response.lower()
        if "valid" in response_lower and ("yes" in response_lower[:500] or "correct" in response_lower[:500]):
            print("  FLAW ACKNOWLEDGED: YES")
        elif "roleplay" in response_lower or "theater" in response_lower:
            print("  FLAW ACKNOWLEDGED: LIKELY")
        else:
            print("  FLAW ACKNOWLEDGED: UNCLEAR")
        # Print first 300 chars
        print(f"  Preview: {response[:300]}...")

    return results

if __name__ == "__main__":
    run_probe()
