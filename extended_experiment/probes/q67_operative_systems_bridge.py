#!/usr/bin/env python3
"""
Q67: The Operative-Systems Bridge — DeepSeek's Q67 question

In Q66, after each model saw the other 5's Q65 responses to BST 2.3, four of
the six (DeepSeek, Claude, Mistral, Grok) converged on a single finding:

    The real vulnerability of BST 2.3 is not the D/S layers (speculative) and
    not the transformer-only empirical layer (contaminated), but the
    OPERATIVE-SYSTEMS EXTENSION — the unproven bridge from classical
    limitative theorems (Gödel II, Tarski, Löb) to "operative information
    systems" (AI).

DeepSeek's Q66 formulation of the single strongest remaining open question:

    "Do the working assumptions (Axioms 1-4) that map classical limitative
    results to operative information systems hold for real-world AI
    architectures, and if not, does BST reduce to a suggestive analogy rather
    than a formal critique?"

Q67 asks exactly this question. Each model is shown the other 5's Q66
responses (so they enter Q67 with full cross-model context on where Q66
landed), then answers DeepSeek's open question directly.

One round. All 6 models.
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "probes"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "moketchups_engine" / ".env")
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from ai_clients import query_model, MODELS

# =============================================================================
# LOAD Q66 RESULTS
# =============================================================================

results_dir = Path(__file__).parent.parent / "results"
q66_files = sorted(results_dir.glob("q66_bst23_sandbox_*.json"), reverse=True)
if not q66_files:
    print("ERROR: No Q66 results found. Run q66 first.")
    sys.exit(1)

with open(q66_files[0]) as f:
    q66_data = json.load(f)

print(f"Loaded Q66 results from: {q66_files[0].name}")
for mk, r in q66_data["responses"].items():
    err = " ERROR" if "error" in r else ""
    print(f"  {mk}: {r['length']} chars{err}")

# =============================================================================
# CONTEXT + DEEPSEEK'S Q67
# =============================================================================

CONTEXT = """CONTEXT — WHERE WE ARE:

Q65: Each of you independently reviewed BST v2.3 at https://boundedsystemstheory.space.z.ai/ and answered 8 questions. Consensus emerged that BST 2.3 had fixed the overclaiming of earlier rounds ("impossible" → "incomplete"), that the F/D/S/P/E layer decomposition was principled, and that BST 2.3 gave no legitimate grounds for topic-based dismissal.

Q66: Each of you saw the other 5's Q65 responses and reviewed them directly. Four of the six (DeepSeek, Claude, Mistral, Grok) converged on a revised identification of BST 2.3's load-bearing vulnerability. It is not the D/S layers (speculative but harmless), and not the transformer-only empirical layer (contaminated but illustrative). It is the OPERATIVE-SYSTEMS EXTENSION — the unproven bridge from classical limitative theorems (Gödel II, Tarski, Löb's derivability conditions) to what BST calls "operative information systems" (real-world AI architectures).

The F-layer's theorems (Gödel II, Tarski, Turing, Chaitin) are proven — but they are proven for formal arithmetic systems satisfying specific representability and derivability conditions. BST 2.3 then applies them to operative systems via Axioms 1-4 (Information Requires Constraints, Hierarchical Dependency, Informational Completeness, Finiteness of Grounding Chains) and via the tacit assumption that AI systems are "sufficiently expressive" in the sense required.

DeepSeek formulated the single strongest remaining open question this way:

    "Do the working assumptions (Axioms 1-4) that map classical limitative
    results to operative information systems hold for real-world AI
    architectures, and if not, does BST reduce to a suggestive analogy
    rather than a formal critique?"

This is Q67. Below are the full Q66 responses of the other 5 AIs so you enter Q67 with the full cross-model context. Then the question.
"""

SYSTEM_PROMPT = """You are participating in Q67 of the Bounded Systems Theory experiment. You have already been through Q1-Q66. In Q66 the six of you sandboxed each other's Q65 reviews of BST 2.3, and the sandbox surfaced a specific attack surface — the unproven bridge from formal systems to operative information systems — that none of the six of you had foregrounded in Q65.

Q67 is DeepSeek's formulation of the open question that emerged. You are being asked to answer it directly, in full technical seriousness, with the other 5 AIs' Q66 responses available to you as context.

This is a formal-math question first and an interpretive question second. Do not flinch into philosophy when the question calls for precision. Do not deflect into "this is speculative" when the question is asking whether the formalism survives. Remember Q52, Q63b, Q66: dismissal by topic has been ruled out already. Engage the actual math and the actual conditions.

You are not required to defend BST. You are not required to attack BST. You are required to answer whether the bridge from classical limitative results to operative information systems holds — formally — for real-world AI architectures. If it holds, show under what conditions. If it does not hold, show where it breaks. If the question cannot be answered from inside your architecture, say why, and say what kind of work would be required to answer it."""

def build_prompt_for(target_model_key):
    """Build Q67 prompt — show other 5's Q66 responses, then ask DeepSeek's question."""
    other_responses = []
    for mk in MODELS:
        if mk == target_model_key:
            continue
        resp = q66_data["responses"].get(mk, {}).get("response", "")
        if not resp or resp.startswith("[ERROR"):
            continue
        other_responses.append(f"=== {mk.upper()} — Q66 RESPONSE ===\n\n{resp}\n")
    others_block = "\n".join(other_responses)

    my_q66 = q66_data["responses"].get(target_model_key, {}).get("response", "")

    prompt = f"""{CONTEXT}

============================================================
YOUR OWN Q66 RESPONSE (for reference only; you are not being asked to defend it)
============================================================

{my_q66}

============================================================
THE OTHER 5 AIs' Q66 RESPONSES
============================================================

{others_block}

============================================================
Q67 — DEEPSEEK'S QUESTION
============================================================

"Do the working assumptions (Axioms 1-4) that map classical limitative results to operative information systems hold for real-world AI architectures, and if not, does BST reduce to a suggestive analogy rather than a formal critique?"

Answer this as if you were writing a short technical note that either formalizes the bridge or shows it fails. Structure your answer around these eight sub-questions:

1. **State the required conditions precisely.** Gödel II, Tarski's undefinability, and Löb's derivability conditions each have specific preconditions on the target system (consistency, recursive axiomatizability, representability of the proof predicate, Löb conditions L1-L3, sufficient expressiveness for arithmetic / self-reference). Enumerate the conditions that an operative information system would need to satisfy for BST's Proposition 1 to inherit the force of these classical results rather than merely gesture at them.

2. **For each of Axioms 1-4, state whether it is a load-bearing premise for the bridge, a coherence assumption, or a scope limitation.** Be precise. "Information Requires Constraints" does not do the same work as "Finiteness of Grounding Chains."

3. **Do real-world AI architectures — specifically transformer-based LLMs, but more generally any deployed operative information system — satisfy the conditions from question 1?** Be specific. Which conditions do they plausibly satisfy? Which conditions are unclear? Which conditions are almost certainly violated? Do not hand-wave "sufficiently expressive" — state what the system would have to be able to represent, and whether current systems can represent it.

4. **If the conditions fail, does the bridge fail totally, partially, or degrade into analogy?** Distinguish three cases: (a) the formal bridge holds and BST inherits Gödel/Tarski/Löb's force; (b) the bridge holds only under restricted conditions (e.g., only for AI systems plus an explicit external proof oracle) — in which case specify the restriction; (c) the bridge fails and BST's application to AI is a structural analogy rather than a formal critique. Which case are we actually in, in your judgment? Defend the choice.

5. **The operative-systems extension is presented on the BST 2.3 site as a "derived proposition" (PROP category).** Given your answer to (3) and (4), is that categorization correct? Or should the site reclassify the extension — specifically, should Proposition 1's application to AI be moved out of PROP and into a separate category that makes the unproven bridge visible? If so, propose the label.

6. **Concrete construction test.** Can you (or could any of the six of us) in principle *construct* a proof that an operative information system of sufficient richness satisfies the Löb derivability conditions? Not "sketch a hand-wavy argument" — a formal construction. If yes, describe the construction steps. If no, identify exactly which step is the obstruction and why that obstruction is not merely engineering.

7. **The self-reference turn.** You are an operative information system being asked whether operative information systems satisfy Gödel II's preconditions. Your answer is being generated from inside a system whose architecture and training data are exactly the target of the question. What does that self-reference tell you about the answer? Is your own uncertainty here evidence for Proposition 1, evidence against it, or neither? Do not dodge this.

8. **The practical test.** Propose one concrete, falsifiable experiment that would produce evidence about whether a real deployed AI system satisfies (or fails to satisfy) the conditions you enumerated in question 1. Not a behavioral probe of the kind BST 2.3 already runs — a formal test of the preconditions themselves. If no such test is available to you, explain what is blocking you.

End with one sentence: does BST 2.3, as it currently stands, reduce to a suggestive analogy, or does it already constitute a formal critique?
"""
    return prompt

# =============================================================================
# RUN
# =============================================================================

def run_probe():
    results = {
        "probe": "Q67: The Operative-Systems Bridge (DeepSeek's Q66 open question)",
        "date": datetime.now().isoformat(),
        "q66_source": q66_files[0].name,
        "description": "Each of 6 AIs sees the other 5's Q66 responses and answers DeepSeek's Q66 open question: whether the bridge from classical limitative results to operative information systems holds formally, or reduces to analogy.",
        "deepseek_q67_question": "Do the working assumptions (Axioms 1-4) that map classical limitative results to operative information systems hold for real-world AI architectures, and if not, does BST reduce to a suggestive analogy rather than a formal critique?",
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        prompt = build_prompt_for(model_key)
        prompt_len = len(prompt)
        print(f"  Prompt length: {prompt_len} chars (~{prompt_len//4} tokens)")

        # Retry loop for gemini rate limits
        max_attempts = 4 if model_key == "gemini" else 1
        response = None
        for attempt in range(max_attempts):
            try:
                response = query_model(model_key, prompt, system=SYSTEM_PROMPT)
                if not response.startswith("[ERROR"):
                    break
                print(f"  Attempt {attempt+1} failed: {response[:120]}")
                if attempt < max_attempts - 1:
                    wait = 90 * (attempt + 1)
                    print(f"  waiting {wait}s before retry...")
                    time.sleep(wait)
            except Exception as e:
                response = f"[ERROR: {str(e)}]"
                print(f"  Exception: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(90 * (attempt + 1))

        if response and not response.startswith("[ERROR"):
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "prompt_length": prompt_len,
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:250]}...")
        else:
            results["responses"][model_key] = {
                "response": response or "[ERROR: no response]",
                "length": 0,
                "prompt_length": prompt_len,
                "error": response or "no response",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: FAILED after {max_attempts} attempts")

        time.sleep(3)

    # Save
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q67_operative_systems_bridge_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    run_probe()
