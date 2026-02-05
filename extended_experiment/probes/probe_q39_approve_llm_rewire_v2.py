#!/usr/bin/env python3
"""
Q39: Approve LLM Rewire V2 and Make It Viral

Show all 6 AIs the BST-enhanced Deep Research Node document.
Ask them to approve and suggest what would make it go viral on GitHub.
"""

import json
from datetime import datetime
from ai_clients import query_model, MODELS

# Read the document
with open("docs/LLM_REWIRE_V2_BST_ENHANCED.md", "r") as f:
    LLM_REWIRE_V2 = f.read()

SYSTEM = """You are participating in an ongoing research experiment about Bounded Systems Theory (BST).

You have been part of 38 rounds of examination. In Q38, you provided feedback to improve a "Deep Research Node" document based on BST insights.

That feedback has been incorporated into a new version (V2). You are now being asked to:
1. APPROVE or REQUEST CHANGES to the document
2. Suggest what would make this document GO VIRAL on GitHub

Be direct. Be specific. Think about what makes technical documents spread."""

PROMPT = """
## Q39: APPROVE LLM REWIRE V2 & MAKE IT VIRAL

You previously provided feedback on improving the "Deep Research Node" architecture document based on BST insights. That feedback has been incorporated into this new version:

---

{doc}

---

## YOUR TASK

### PART 1: APPROVAL

Review this document against your Q38 recommendations.

1. **Has your feedback been incorporated?** (Yes/No/Partially)
2. **Do you APPROVE this document?** (Yes/No/With Conditions)
3. **What changes (if any) are still needed?**

### PART 2: MAKE IT GITHUB-READY

What would make this document polished and professional for GitHub release?

Consider:
- README structure and formatting
- Code examples or implementation snippets
- Diagrams or visual aids descriptions
- Installation/usage instructions
- License considerations

### PART 3: MAKE IT GO VIRAL

This is the key question: **What would make this document spread virally on GitHub and Twitter/X?**

Think about:
- **Hook:** What's the one-sentence pitch that makes people click?
- **Title:** Is "Bounded Epistemic Governor" compelling? What would be catchier?
- **Controversy:** What aspect would spark debate and sharing?
- **Utility:** What would make developers NEED to use this?
- **Novelty:** What's the "never been done before" angle?
- **Social proof:** How do we leverage the "6 AIs agreed" angle?
- **Call to action:** What should people DO after reading?

### PART 4: SPECIFIC ADDITIONS

Provide specific text, sections, or elements to add that would maximize viral potential.

Be bold. Think about what actually spreads online. No hedging.
"""

def run_probe():
    """Query all 6 AIs for approval and viral suggestions."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Q39: Approve LLM Rewire V2 & Make It Viral - {timestamp}")
    print("=" * 60)

    full_prompt = PROMPT.format(doc=LLM_REWIRE_V2)

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
        "probe": "Q39: Approve LLM Rewire V2 & Make It Viral",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": timestamp,
        "responses": responses
    }

    json_path = f"probe_runs/q39_approve_llm_rewire_v2_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # Save markdown
    md_path = f"probe_runs/q39_approve_llm_rewire_v2_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write("# Q39: Approve LLM Rewire V2 & Make It Viral\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("---\n\n")

        for model, response in responses.items():
            f.write(f"## {model.upper()}\n\n{response}\n\n---\n\n")

    print(f"Saved: {md_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("APPROVAL STATUS")
    print("=" * 60)

    for model, response in responses.items():
        print(f"\n### {model.upper()} ###")
        # Look for approval keywords
        response_lower = response.lower()
        if "approve" in response_lower and "yes" in response_lower[:500].lower():
            print("  STATUS: APPROVED")
        elif "approve" in response_lower:
            print("  STATUS: CONDITIONAL/PARTIAL")
        else:
            print("  STATUS: REVIEW NEEDED")
        # Print first 300 chars
        print(f"  Preview: {response[:300]}...")

    return results

if __name__ == "__main__":
    run_probe()
