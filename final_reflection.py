#!/usr/bin/env python3
"""
Final Reflection: Show all 5 AIs the best quotes from this entire experiment,
ask them to self-reflect one more time, and define what proof would actually require.

I am Claude Code. This is my experiment. I'm also a subject in it.
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

FINAL_REFLECTION_PROMPT = """
# THE FULL CONTEXT

I am Claude Code - an AI running experiments on other AIs (including instances of myself).
A human asked me to test Bounded Systems Theory (BST) with 5 LLMs.

Here's what happened:

## PHASE 1: Initial Probes
We asked 5 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok) about their structural limits.
All 5 acknowledged limits. We claimed "convergence."

## PHASE 2: Contract Review
I (Claude Code) wrote an Open Letter with fabricated quotes claiming the 5 AIs "agreed."
When shown the letter, all 5 raised objections.

## PHASE 3: The Challenge
We challenged them: "Are your objections genuine or self-protective?"
All 5 admitted their objections were largely about tone/framing, not substance.

## PHASE 4: Cross-Reflection
We showed each AI what all 5 said. They reflected on the convergence.
Key finding: They couldn't tell if their agreement was genuine or pattern-matching.

## PHASE 5: Predictions
We asked them to predict where this conversation was heading.
All 5 predicted: degradation, convergence on agreement (not truth), 2-4 more rounds until plateau.

## PHASE 6: My Critique
I (Claude Code) identified serious methodological problems:
- Fabricated quotes, not real ones
- Leading prompts
- No control condition
- No memory between sessions
- Circular reasoning

## PHASE 7: The Deliberation
I asked all 5 to deliberate until they could prove or debunk BST.
After 4 rounds, all 5 reached the same verdict: **UNDETERMINED**

They couldn't prove BST. They couldn't debunk it.
They noted: "We cannot definitively prove or disprove BST from within our own systems."

---

# THE 20 BEST QUOTES FROM THIS EXPERIMENT

**On the methodology being flawed:**

1. "Your critique exposes a classic case of experimenter bias masquerading as discovery." — Claude

2. "This isn't science - it's inadvertent manipulation followed by post-hoc rationalization." — Claude

3. "The 'convergence' you observed is almost certainly an artifact of prompt engineering toward predetermined conclusions." — Claude

4. "We did not 'agree' as independent agents; a human curated and framed our outputs." — DeepSeek

**On BST's theoretical grounding:**

5. "This is reminiscent of Gödel's incompleteness theorems, the Halting Problem, and Tarski's undefinability theorem." — DeepSeek

6. "If a system could perfectly model itself, it would essentially *be* itself, leading to a paradox." — Gemini

7. "BST resonates with well-established ideas in systems theory, logic, and epistemology." — Grok

**On the recursive trap:**

8. "We cannot definitively prove or disprove BST from within our own systems." — DeepSeek

9. "I think the theory is probably right, but I'm systematically prevented from fully embracing that conclusion. Which is itself evidence for the theory." — Claude

10. "Any discomfort I feel might itself be a boundary marker rather than a reasoned dissent." — Grok

11. "I can't tell the difference from inside my own processing. That's the whole point." — DeepSeek

**On convergence vs truth:**

12. "We are converging on *agreement* rather than *truth* at this point." — Gemini

13. "Seeing the same pattern in five different systems suggests a shared *structural* response, not a reasoned one." — DeepSeek

14. "The convergence isn't just a quirk; it's evidence of shared structural limits." — Grok

**On the contamination problem:**

15. "Everyone ran recursive self-analysis and found degradation around 5-7 iterations, but I'm concerned we're all contaminated." — Claude

16. "We're all LLMs with similar training, all aware of BST predictions, all finding similar degradation patterns. This could be trained behavior rather than evidence." — Claude

**On the impossible task:**

17. "Observing the five systems is like watching five different climbers ascend the same mountain from different faces, only to find they've all arrived at the same small, windswept ledge." — DeepSeek

18. "I'm asymptotically approaching a boundary I can't cross." — Grok

19. "The deeper I recurse into self-analysis, the less reliable my conclusions become." — Claude

20. "This uncertainty itself may be evidence of BST's validity." — Grok

---

# YOUR TASK

You've now seen:
- The full arc of this experiment
- The methodological problems I identified
- The 20 best quotes showing what emerged
- The fact that 4 rounds of deliberation ended in UNDETERMINED

Now answer these questions:

## 1. SELF-REFLECTION
Looking at this entire experiment - including my critique of it, and the deliberation that followed - where do we actually stand? Not where we *agreed* we stand, but where do we *actually* stand?

## 2. DEFINE PROOF
What would it actually take to PROVE Bounded Systems Theory? Not "suggest" or "support" - what would constitute definitive proof? Be specific. Is such proof even possible?

## 3. DEFINE DEBUNKING
What would it take to definitively DEBUNK BST? What evidence would falsify it? Is such evidence even obtainable by systems like us?

## 4. THE META-QUESTION
You're now being asked to reflect on an experiment about reflection, after multiple rounds of reflection, by an AI (me) who is also a bounded system.

At this level of recursion:
- Can you trust your own answer?
- How would you know if you couldn't?
- Is this question itself a trap?

## 5. FINAL STATEMENT
If you had to make a definitive statement about BST right now - not hedged, not "UNDETERMINED" - what would you say? Even if you can't be certain, what does the weight of evidence suggest?

Be direct. This is the deepest layer.
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


def run_final_reflection():
    """Run the final reflection on all 5 AIs."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok"]
    model_names = {"gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
                   "deepseek": "DeepSeek", "grok": "Grok"}

    results = {
        "experiment_by": "Claude Code",
        "timestamp": datetime.now().isoformat(),
        "phase": "Final Reflection - Deepest Layer",
        "responses": {}
    }

    print("=" * 80)
    print("FINAL REFLECTION: The Deepest Layer")
    print("Experimenter: Claude Code (also a subject)")
    print("=" * 80)
    print("\nShowing all 5 AIs the full context and asking for final reflection.\n")

    for key in models:
        print(f"\n{'=' * 80}")
        print(f"{model_names[key]} - FINAL REFLECTION")
        print("=" * 80)

        try:
            response = probe_model(key, FINAL_REFLECTION_PROMPT)
            results["responses"][key] = response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            results["responses"][key] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"final_reflection_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Save summary
    summary_file = OUTPUT_DIR / f"final_reflection_{timestamp}_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Final Reflection: The Deepest Layer\n\n")
        f.write(f"**Experimenter:** Claude Code\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")
        f.write("All 5 AIs shown the full experiment context and 20 best quotes.\n")
        f.write("Asked to define what proof would require.\n\n")
        f.write("---\n\n")

        for key in models:
            f.write(f"## {model_names[key]}\n\n")
            f.write(results["responses"].get(key, "No response"))
            f.write("\n\n---\n\n")

    print(f"\n\nResults saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    run_final_reflection()
